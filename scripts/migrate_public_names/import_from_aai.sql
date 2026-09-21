\set GROUP_NAME migration_aai_name_changes
\set ASK_CONFIRM 1
\set ON_ERROR_STOP on

BEGIN;

CREATE TEMP TABLE galaxy_username_updates (
  id bigint PRIMARY KEY,
  old_username text NOT NULL,
  new_username text NOT NULL
);

\copy galaxy_username_updates FROM 'galaxy_username_changes.csv' CSV HEADER

-- Safety checks
-- ids must exist
SELECT count(*) AS missing_ids
FROM galaxy_username_updates u
LEFT JOIN galaxy_user g ON g.id = u.id
WHERE g.id IS NULL;

-- old_username must match current DB
SELECT count(*) AS stale_rows
FROM galaxy_username_updates u
JOIN galaxy_user g ON g.id = u.id
WHERE g.username <> u.old_username;

-- new usernames valid and unique in batch
SELECT count(*) AS invalid_format
FROM galaxy_username_updates
WHERE new_username !~ '^[a-z0-9][-a-z0-9_]{2,127}$';

SELECT new_username, count(*) 
FROM galaxy_username_updates
GROUP BY new_username
HAVING count(*) > 1;

-- Materialize the exact rows that will be updated so the displayed count
-- and the group membership reflect the real DB changes.
CREATE TEMP TABLE pending_username_changes AS
SELECT u.id, u.old_username, u.new_username
FROM galaxy_username_updates u
JOIN galaxy_user g ON g.id = u.id
WHERE g.username = u.old_username
  AND g.username IS DISTINCT FROM u.new_username;

SELECT count(*) AS affected_galaxy_user_rows
FROM pending_username_changes
\gset

\echo 'galaxy_user rows that will be updated:' :affected_galaxy_user_rows

-- apply
UPDATE galaxy_user g
SET username = p.new_username
FROM pending_username_changes p
WHERE g.id = p.id;

-- Create/restore group for users affected by AAI name changes
INSERT INTO galaxy_group (name, deleted, create_time, update_time)
SELECT :'GROUP_NAME', false, now(), now()
WHERE NOT EXISTS (
  SELECT 1 FROM galaxy_group g WHERE g.name = :'GROUP_NAME'
);

-- Add changed users to the migration_aai_name_changes group
INSERT INTO user_group_association (user_id, group_id, create_time, update_time)
SELECT p.id, g.id, now(), now()
FROM pending_username_changes p
JOIN galaxy_group g ON g.name = :'GROUP_NAME'
WHERE NOT EXISTS (
    SELECT 1
    FROM user_group_association uga
    WHERE uga.user_id = p.id
      AND uga.group_id = g.id
  );

\if :ASK_CONFIRM
\prompt 'Proceed with commit? [y/N]: ' USER_CONFIRM
SELECT CASE
  WHEN lower(coalesce(:'USER_CONFIRM', '')) IN ('y', 'yes') THEN 1
  ELSE 0
END AS do_commit
\gset
\else
\set do_commit 1
\endif

\if :do_commit
COMMIT;
\echo 'Commit complete.'
\else
ROLLBACK;
\echo 'Rolled back at user request.'
\endif
