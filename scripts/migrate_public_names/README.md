# Public name migration script

Removes invalid characters, dedupes and makes sure public names conform to constraints.

### Usage:

```
# switch to any writable directory
cd /tmp
# run migration script
psql -f migrate_public_names.sql
```

* By default, the script runs in dry-run mode, so no modifications are made to the database.
* Edit migrate.sql and toggle COMMIT_MODE to 1 if you want to actually commit the changes.
* In commit mode, a database constraint is also added to the database to ensure future public names will conform.

### Output:

```
JSON report: migration_report.json
CSV mapping: migration_mapping.csv
```

* The migration_mapping_tmp table is preserved for easy querying, and can be dropped after migration.
* In COMMIT_MODE, galaxy_user_backup_<timestamp> and migration_mapping_backup_<timestamp> tables are generated per run,
  and can be dropped when no longer required.

### Notes
* Make sure the script is run from a writable directory, so output reports can be written.
* Drop the migration_mapping_tmp table if no longer required.
* Drop the galaxy_user_backup_<timestamp> table and migration_mapping_backup_<timestamp> table if no longer required.


Migration day notes

1. Make a copy of the galaxy_user table named galaxy_user_backup: `CREATE TABLE galaxy_user_backup AS TABLE galaxy_user;`
2. Run the migration script in dry-run mode: `psql -f migrate_public_names.sql`
3. Set COMMIT mode to 1
4. Run the migration script in commit mode: `psql -f migrate_public_names.sql`
5. Copy the output indicating backup tables and store safely for future reference
6. Verify migration by running `select count(*) from migration_mapping_tmp where change_type != 'unchanged';`
7. Export galaxy_user table `\copy (SELECT * FROM galaxy_user where purged = false) TO 'galaxy_user.csv' WITH CSV HEADER;`
8. Send to Marius
9. Prefix all legacy purged users with double underscore - new ones are already obfuscated: `psql -f update_purged_usernames.sql`
10. Place 'galaxy_username_changes.csv' in a folder accessible to psql.
11. Run `psql -f import_from_aai.sql`. The script assumes that 'galaxy_username_changes.csv' is in current folder.
12. Export galaxy_user table again `\copy (SELECT * FROM galaxy_user where purged = false) TO 'galaxy_user_final.csv' WITH CSV HEADER;`
13. Send to Marius