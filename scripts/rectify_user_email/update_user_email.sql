\set ON_ERROR_STOP on

-- Set this to 1 if you want to commit, 0 if you want a dry-run
\set COMMIT_MODE 0

-- Check user_id
\if :{?user_id}
    \echo Running for user_id = :user_id
\else
    \echo 'ERROR: user_id not set. Use -v user_id=123'
    \quit 1
\endif

-- Check new_email
\if :{?new_email}
    \echo New email = :new_email
\else
    \echo "ERROR: new_email not set. Use -v new_email='user@example.org'"
    \quit 1
\endif

BEGIN;
UPDATE galaxy_user set email = :'new_email' where id = :user_id;

\if :COMMIT_MODE
COMMIT;
\else
\echo 'Set COMMIT_MODE to 1 to commit changes'
ROLLBACK;
\endif
