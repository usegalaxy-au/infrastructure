-- Set this to 1 if you want to commit, 0 if you want a dry-run
\set COMMIT_MODE 0

\set ON_ERROR_STOP on

DROP TABLE IF EXISTS migration_mapping_tmp;

-- perform actions on a copy of the table
--DROP TABLE IF EXISTS copy_galaxy_user;
--CREATE TABLE copy_galaxy_user AS SELECT * FROM galaxy_user;

BEGIN;

\if :COMMIT_MODE
CREATE TEMP TABLE migration_run_ts (run_ts text) ON COMMIT DROP;
INSERT INTO migration_run_ts (run_ts)
VALUES (to_char(clock_timestamp(), 'YYYYMMDD_HH24MISSMS'));
\endif

-- 1) Build temp table with proposed mappings
CREATE TABLE migration_mapping_tmp AS
WITH norm AS (
  SELECT u.id, u.username AS old_username,
         lower(regexp_replace(u.username, '[\s.]', '_', 'g')) AS s1
  FROM galaxy_user u
),
clean AS (
  SELECT id, old_username, regexp_replace(s1, '[^a-z0-9_-]', '_', 'g') AS s2
  FROM norm
),
start_ok AS (
  SELECT id, old_username, regexp_replace(s2, '^[^a-z0-9]+', '') AS s3
  FROM clean
),
seeded AS (
  SELECT id, old_username,
         CASE WHEN s3 = '' THEN 'u' || id::text ELSE s3 END AS base0
  FROM start_ok
),
minlen AS (
  SELECT id, old_username,
         CASE WHEN length(base0) < 3 THEN base0 || repeat('_', 3 - length(base0)) ELSE base0 END AS base
  FROM seeded
),
dedup AS (
  SELECT base, count(*) AS grp_size
  FROM minlen
  GROUP BY base
),
ranked AS (
  SELECT m.id, m.old_username, m.base, d.grp_size,
         row_number() OVER (PARTITION BY m.base ORDER BY m.id) AS rn
  FROM minlen m
  JOIN dedup d USING (base)
),
proposed AS (
  SELECT id, old_username, base, grp_size, rn,
         CASE
           WHEN grp_size = 1 THEN left(base, 128)
           ELSE left(base, 128 - (1 + length(rn::text)))
         END AS base_trunc
  FROM ranked
)
SELECT
  id,
  old_username,
  CASE WHEN grp_size = 1 THEN base_trunc ELSE base_trunc || '_' || rn::text END AS new_username,
  CASE
    WHEN grp_size = 1 AND old_username = base_trunc THEN 'unchanged'
    WHEN grp_size = 1 THEN 'normalized_only'
    ELSE 'collision_suffix_added'
  END AS change_type
FROM proposed;

-- In commit mode, persist a full backup of the original user table per run
\if :COMMIT_MODE
DO $$
DECLARE
  v_run_ts text;
  v_backup_table text;
BEGIN
  SELECT run_ts INTO v_run_ts FROM migration_run_ts;
  v_backup_table := 'galaxy_user_backup_' || v_run_ts;
  EXECUTE format('CREATE TABLE %I AS TABLE galaxy_user', v_backup_table);
  RAISE NOTICE 'Created backup user table: %', v_backup_table;
END $$;
\endif

-- 2) Apply the update on the scratch table for REAL validation
SAVEPOINT do_update;

UPDATE galaxy_user g
SET username = m.new_username
FROM migration_mapping_tmp m
WHERE g.id = m.id;

-- 3) Validate: fail if regex violations or duplicates exist
DO $$
DECLARE
  v_nonmatching int;
  v_dup_groups int;
BEGIN
  SELECT count(*) INTO v_nonmatching
  FROM galaxy_user
  WHERE username !~ '^[a-z0-9][-a-z0-9_]{2,127}$';

  IF v_nonmatching > 0 THEN
    RAISE EXCEPTION 'Validation failed: % usernames do not match new regex', v_nonmatching
      USING ERRCODE = 'check_violation';
  END IF;

  SELECT count(*) INTO v_dup_groups
  FROM (
    SELECT username
    FROM galaxy_user
    GROUP BY username
    HAVING count(*) > 1
  ) s;

  IF v_dup_groups > 0 THEN
    RAISE EXCEPTION 'Validation failed: % duplicate username groups found', v_dup_groups
      USING ERRCODE = 'unique_violation';
  END IF;
END $$;

-- In commit mode, persist a backup mapping table per run for rollback/inspection
\if :COMMIT_MODE
DO $$
DECLARE
  v_run_ts text;
  v_backup_table text;
BEGIN
  SELECT run_ts INTO v_run_ts FROM migration_run_ts;
  v_backup_table := 'migration_mapping_backup_' || v_run_ts;
  EXECUTE format('CREATE TABLE %I AS TABLE migration_mapping_tmp', v_backup_table);
  RAISE NOTICE 'Created backup mapping table: %', v_backup_table;
END $$;
\endif

-- Build a compact JSON report into a TEMP TABLE
CREATE TEMP TABLE migration_report_tmp AS
WITH summary AS (
  SELECT
    (SELECT count(*) FROM migration_mapping_tmp) AS total_users,
    (SELECT count(*) FROM migration_mapping_tmp WHERE old_username <> new_username) AS changed_count,
    round(
      100.0 * (SELECT count(*) FROM migration_mapping_tmp WHERE old_username <> new_username)::numeric
      / NULLIF((SELECT count(*) FROM migration_mapping_tmp), 0), 2
    ) AS changed_pct,
    (SELECT count(*) FROM migration_mapping_tmp WHERE change_type = 'collision_suffix_added') AS collision_suffixes,
    (SELECT count(*) FROM migration_mapping_tmp WHERE change_type = 'normalized_only') AS normalized_only,
    (SELECT count(*) FROM migration_mapping_tmp WHERE change_type = 'unchanged') AS unchanged_count
),
dupes AS (
  SELECT username, count(*) AS n
  FROM galaxy_user
  GROUP BY username
  HAVING count(*) > 1
),
nonmatch AS (
  SELECT count(*) AS post_nonmatching_count
  FROM galaxy_user
  WHERE username !~ '^[a-z0-9][-a-z0-9_]{2,127}$'
)
SELECT jsonb_build_object(
  'summary', jsonb_build_object(
      'total_users', (SELECT total_users FROM summary),
      'changed_count', (SELECT changed_count FROM summary),
      'changed_pct', (SELECT changed_pct FROM summary),
      'collision_suffixes', (SELECT collision_suffixes FROM summary),
      'normalized_only', (SELECT normalized_only FROM summary),
      'unchanged_count', (SELECT unchanged_count FROM summary),
      'post_update_nonmatching_regex_count', (SELECT post_nonmatching_count FROM nonmatch),
      'post_update_duplicate_groups', COALESCE((
          SELECT jsonb_agg(jsonb_build_object('username', username, 'count', n)) FROM dupes
      ), '[]'::jsonb)
  ),
  'details', COALESCE((
      SELECT jsonb_agg(jsonb_build_object(
        'id', id,
        'old_username', old_username,
        'new_username', new_username,
        'change_type', change_type
      ) ORDER BY id)
      FROM migration_mapping_tmp
      WHERE change_type != 'unchanged'
  ), '[]'::jsonb)
) AS report;

-- if COMMIT_MODE == 1
\if :COMMIT_MODE
COMMIT;
\echo 'Commit complete.'
ALTER TABLE galaxy_user DROP CONSTRAINT IF EXISTS username_format_chk;
ALTER TABLE galaxy_user
  ADD CONSTRAINT username_format_chk
  CHECK (username ~ '^[a-z0-9][-a-z0-9_]{2,127}$');
\echo 'Constraint added to prevent future deviations.'
\else
ROLLBACK TO do_update;
COMMIT;
\echo 'Dry-run complete.'
\endif

-- EXPORTS (run after transaction so report write failures do not roll back data)
\copy migration_report_tmp TO 'migration_report.json'
\copy (SELECT id, old_username, new_username, change_type FROM migration_mapping_tmp WHERE change_type != 'unchanged' ORDER BY id ) TO 'migration_mapping.csv' CSV HEADER

\echo 'JSON report: migration_report.json'
\echo 'CSV mapping: migration_mapping.csv'
