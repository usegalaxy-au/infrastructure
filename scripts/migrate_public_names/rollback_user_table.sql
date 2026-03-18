-- before running, update the galaxy_user_backup_<timestamp> to the correct table
-- Set this to 1 if you want to commit, 0 if you want a dry-run
\set COMMIT_MODE 0

BEGIN;
UPDATE galaxy_user g
SET username = b.new_username
FROM galaxy_user_backup_<timestamp> b
WHERE g.id = b.id;

\if :COMMIT_MODE
COMMIT;
\else
\echo 'Set COMMIT_MODE to 1 to commit changes'
ROLLBACK;
\endif
