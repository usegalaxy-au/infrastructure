\set ON_ERROR_STOP on

-- Set this to 1 if you want to commit, 0 if you want a dry-run
\set COMMIT_MODE 0

-- Require user_id to be provided
\if :{?user_id}
    \echo Running for user_id = :user_id
\else
    \echo 'ERROR: user_id not set. Use -v user_id=123'
    \quit 1
\endif

BEGIN;
UPDATE galaxy_session SET is_valid = false WHERE is_valid = true AND user_id = :user_id;

\if :COMMIT_MODE
COMMIT;
\else
\echo 'Set COMMIT_MODE to 1 to commit changes'
ROLLBACK;
\endif
