BEGIN;

CREATE TEMP TABLE galaxy_username_updates (
  id bigint PRIMARY KEY,
  old_username text NOT NULL,
  new_username text NOT NULL
);

\copy galaxy_username_updates
FROM '/path/to/galaxy_username_changes.csv'
CSV HEADER;

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

-- apply
UPDATE galaxy_user g
SET username = u.new_username
FROM galaxy_username_updates u
WHERE g.id = u.id
  AND g.username = u.old_username
  AND g.username IS DISTINCT FROM u.new_username;

COMMIT;
