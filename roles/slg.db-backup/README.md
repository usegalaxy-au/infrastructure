# db-backup role

Ansible role for setting up a rotating backup system for a postgresql database and optionally sending it to a swift object store

**Author: Simon Gladman 2020**

## Pre-requisites

Python >= 3.6
Python3 venv

## Role Variables

### Paths

**script_path** The location of the backup script and it's virtualenv 
default: '~/galaxy_backup'

**backup_path** The location of the local backups
default: ~/galaxy-backups

**venv_location** The location of the virtual env 
default: "{{ script_path }}/venv"

### DB Settings

**psql_db** The name of the database to backup
default: 'galaxy'

**db_user** The database connection user
default: galaxy

**db_password**: The database connection password
default: ""

**db_server** The FQDN of the database server
default: localhost

**db_port** The database port
default: 5432

### Swift settings

**use_swift** Boolean that flags the use of swift for saving the backups remotely
default: false

**swift_backup_container** The name of the swift container to send the backups to
default: ""

**swift_cred_file** The credentials file to source for the swift connection
default: ""

### Retention time / backup rotation variables

**monthly_backup_day** Day of the month to run the monthly backup on
default: 1

**weekly_backup_day** Weekly backups will run on this day of the week
default: 6

**retention_day** Keep daily backups for this many days
default: 6

**retention_week** Keep weekly backups for this many days (e.g. 21 days = 3 weeks)
default: 21

**retention_month** Keep monthly backups for this many days (e.g. 92 days ~ 3 months)
default: 92

**connection_string** The postgresql formatted db connection string
default: "postgres://{{ db_user }}:{{ db_password }}@{{ db_server }}:{{ db_port }}/{{ psql_db }}"

## Example playbook

- hosts: backupserver
  roles:
    - role: slg.db-backup
      