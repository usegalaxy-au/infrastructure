# Plan: Workflow Invocation Reporting via InfluxDB + Grafana

## Context

Galaxy Australia tracks workflow invocations in nginx logs, but the encoded workflow IDs are user-specific and can't be aggregated directly. A Python script (`extract_workflow_invocations.py`) already exists that decodes these IDs and resolves workflow names via the Galaxy DB. This plan adapts that script to write data into InfluxDB (instead of CSV), deployed as a daily cron job on the Galaxy server, so it can be visualized in Grafana.

Crucially, the script also resolves **canonical workflow identity** using `Workflow.source_metadata`. When a workflow was imported from a TRS registry (Dockstore, WorkflowHub), the `trs_tool_id` field uniquely identifies the original workflow across all user imports. This allows aggregating invocations of the same workflow even when different users have independently imported it.

This follows the exact same pattern as the existing `slg.galaxy_stats` role (e.g. `get_queue_size.py`) and the `post_labs_logs.sh` cron job.

## Changes

### 1. Create new Ansible role `galaxy-workflows-reporting`

**Directory:** `roles/galaxy-workflows-reporting/`

```
roles/galaxy-workflows-reporting/
├── plan.md                    # Implementation plan (this plan, copied here)
├── defaults/main.yml          # Default variables
├── templates/
│   ├── collect_workflow_invocations.py.j2   # Main Python script
│   └── collect_workflow_invocations.service.j2  # Systemd unit
├── files/
│   └── requirements.txt       # Python dependencies
└── tasks/main.yml             # Role tasks
```

#### `defaults/main.yml`

```yaml
workflow_invocations_dir: /home/ubuntu/workflow_invocations
workflow_invocations_venv: "{{ workflow_invocations_dir }}/venv"
workflow_invocations_influxdb_database: workflow_invocations
```

#### `files/requirements.txt`

```
influxdb
pycryptodome
sqlalchemy
psycopg2-binary
```

#### `templates/collect_workflow_invocations.py.j2`

Adapted from `extract_workflow_invocations.py` with these changes:
- Reads nginx log lines from **stdin** (streaming) — designed to be piped from `tail -F`
- Writes each invocation to InfluxDB immediately using the `influxdb` Python client (same as [get_queue_size.py.j2](roles/slg.galaxy_stats/templates/get_queue_size.py.j2))
- Reads InfluxDB credentials from the existing [secret.yml](roles/slg.galaxy_stats/templates/secret.yml.j2) at `{{ stats_dir }}/secret.yml`, overriding the database to `workflow_invocations`
- Templates in `GALAXY_ID_SECRET` and `GALAXY_DATABASE_URL` from vault vars
- Resolves canonical workflow identity from `source_metadata` (see below)
- Shebang: `#!{{ workflow_invocations_venv }}/bin/python`

**Canonical identity resolution** (from `Workflow.source_metadata`):

| `source_metadata` state | `canonical_id` tag value |
|---|---|
| Has `trs_tool_id` | `{trs_server}:{trs_tool_id}` |
| Has `url` only | The import URL |
| `NULL` / empty | Workflow name (local workflow, no external origin) |

The `trs_version_id` is stored as a separate field (not part of the canonical ID) so we can group all versions of the same workflow together while still tracking which version was used.

**Updated SQL query:**

```sql
SELECT sw.id, sw.name, sw.user_id, w.uuid, w.source_metadata
FROM stored_workflow sw
JOIN workflow w ON w.id = sw.latest_workflow_id
WHERE sw.id = :id
```

**InfluxDB data model:**
- Measurement: `workflow_invocation`
- Tags (for GROUP BY): `domain`, `workflow_name`, `canonical_id`, `trs_server`
- Fields: `count` (1.0), `workflow_id` (int), `user_id` (int), `trs_version_id` (string)
- Timestamp: parsed from the nginx log line

This allows Grafana queries like:
- Group by `canonical_id` to aggregate invocations across users who imported the same workflow
- Filter by `trs_server` to see Dockstore vs WorkflowHub usage
- Group by `domain` + `canonical_id` to see which lab subdomain drove invocations of which workflow

#### `templates/collect_workflow_invocations.service.j2`

```ini
[Unit]
Description=Collect Galaxy workflow invocations from nginx logs
After=nginx.service

[Service]
ExecStart=/bin/bash -c 'tail -n 0 -F /var/log/nginx/access.log | {{ workflow_invocations_venv }}/bin/python {{ workflow_invocations_dir }}/collect_workflow_invocations.py'
Restart=always
RestartSec=10
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Key details:
- `tail -n 0 -F` starts from the end of the file (no historical replay) and follows through log rotations
- `Restart=always` ensures the service recovers from crashes
- Runs as `ubuntu` user (same as cron jobs)

#### `tasks/main.yml`

1. Create `{{ workflow_invocations_dir }}` directory
2. Copy requirements file
3. Create virtualenv and install dependencies
4. Template the Python script
5. Template the systemd service unit file to `/etc/systemd/system/`
6. Enable and start the service (with handler to restart on config changes)

### 2. Add InfluxDB database + Grafana datasource

**File:** [stats.usegalaxy.org.au.yml](host_vars/stats.usegalaxy.org.au.yml)

- Add `'workflow_invocations'` to `influxdb_databases` list (line ~131)
- Do NOT add to `retention_policy_dbs` (we want infinite retention for this data)
- Add a new Grafana datasource entry for `workflow_invocations` (after line ~384)

### 3. Add role to galaxy_playbook.yml

**File:** [galaxy_playbook.yml](galaxy_playbook.yml) — add `galaxy-workflows-reporting` to the roles list (line ~63, alongside `slg.galaxy_stats`)

### 4. No new secrets needed

The script reuses existing vault variables:
- `vault_aarnet_id_secret` — Galaxy's id_secret for decoding encoded IDs
- Galaxy DB connection via existing reader credentials
- InfluxDB credentials via existing `{{ stats_dir }}/secret.yml`

## Verification

1. Deploy stats playbook: `ansible-playbook stats_playbook.yml` — creates InfluxDB database and Grafana datasource
2. Deploy galaxy playbook: `ansible-playbook galaxy_playbook.yml` — deploys role (script, venv, systemd service)
3. Verify service is running: `systemctl status collect-workflow-invocations`
4. Trigger a test workflow invocation and verify the data point appears in InfluxDB
5. Build Grafana dashboard using the `workflow_invocations` datasource with queries like:
   - Invocations by domain: `SELECT COUNT("count") FROM "workflow_invocation" GROUP BY time($__interval), "domain"`
   - Top workflows (canonical): `SELECT COUNT("count") FROM "workflow_invocation" GROUP BY "canonical_id"`
   - Registry vs local: `SELECT COUNT("count") FROM "workflow_invocation" WHERE "trs_server" != '' GROUP BY "trs_server", time(1d)`
   - Unique users per domain: `SELECT COUNT(DISTINCT("user_id")) FROM "workflow_invocation" GROUP BY "domain", time(1d)`

## Caveats

- `source_metadata` is only populated for TRS and URL imports. Locally-created workflows will have `NULL` source_metadata — these fall back to workflow name as the canonical ID and can't be correlated across users.
- `source_metadata` lives on `Workflow` (revision), not `StoredWorkflow`. The script uses `latest_workflow_id` to get the most recent revision's metadata.
- `Workflow.uuid` is NOT useful for cross-user matching (each import gets a fresh UUID).
