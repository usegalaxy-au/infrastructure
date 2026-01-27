# Public name migration script

Removes invalid characters, dedupes and makes sure public names conform to constraints.

### Usage:

```
# switch to any writable directory
cd /tmp
# run migration script
psql -f migrate.sql
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
