PSQL scripts for fixing a user in the event that their email needs to be changed in Biocommons Access
prior to their first login in galaxy. If this is changed, their email must be changed in the galaxy db
before they verify their email address and log in. This can be done with `update_user_email.sql`.

If the email address is updated in galaxy before the user logs in, **the steps below are not necessary**

However, in the event that the user has already verified the email and logged before the email is updated in galaxy,
some backtracking needs to be done, as an extra galaxy account will be created.
(1) Get user IDs of original account (user_1) and new account (user_2) in galaxy db.
(2) Delete and purge user_2 account from admin UI.
(3) run `psql -v user_id=<user_2 ID> -f invalidate_user_sessions.sql` (set COMMIT_MODE to 1 to commit)
(4) run `psql -v user_id=<user_2 ID> -f remove_user_oidc_entry.sql` (set COMMIT_MODE to 1 to commit)
(5) run `psql -v user_id=<user 1 ID> new_email=<user new email address> -f update_user_email.sql` (set COMMIT_MODE to 1 to commit)

