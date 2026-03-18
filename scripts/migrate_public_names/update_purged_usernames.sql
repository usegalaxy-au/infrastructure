-- Set this to 1 if you want to commit, 0 if you want a dry-run
\set COMMIT_MODE 1

BEGIN;
UPDATE galaxy_user SET username = '__' || username WHERE purged = true AND username ~ '^[^0-9]' AND username !~ '^__';

\if :COMMIT_MODE
COMMIT;
\else
\echo 'Set COMMIT_MODE to 1 to commit changes'
ROLLBACK;
\endif
