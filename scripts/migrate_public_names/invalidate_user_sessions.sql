-- Set this to 1 if you want to commit, 0 if you want a dry-run
\set COMMIT_MODE 1

BEGIN;
UPDATE galaxy_session SET is_valid = false WHERE is_valid = true;

\if :COMMIT_MODE
COMMIT;
\else
\echo 'Set COMMIT_MODE to 1 to commit changes'
ROLLBACK;
\endif
