# grouper

Manages Galaxy Australia group membership: users are added to or removed
from groups automatically based on their email domain, using rules in
`files/approved_domains.json`.

The role installs a small Python package (`grouper`, under `files/grouper/`)
into a host venv, and (optionally) an hourly cron job that runs it under
`flock`.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `grouper_user` | `ubuntu` | Host user that owns and runs grouper |
| `grouper_dir` | `/home/{{ grouper_user }}/grouper` | Where the package, `approved_domains.json`, `users.json` and `grouper.log` live |
| `grouper_venv` | `{{ grouper_dir }}/venv` | Host venv for grouper's runtime dependencies |
| `grouper_run_script_path` | `/home/{{ grouper_user }}/run_groups.sh` | Cron wrapper script (templated from `run_groups.sh.j2`) |
| `grouper_run_log_path` | `/home/{{ grouper_user }}/run_groups.log` | Cron stdout/stderr redirect target - overwritten every run; `grouper.log` (in `grouper_dir`) is the durable, rotated log |
| `grouper_run_args` | `""` | Args passed to `python -m grouper` by `run_groups.sh`, e.g. `"--add --remove --notify --commit"` |
| `grouper_cron_minute` / `grouper_cron_hour` | `"0"` / `"*"` | Cron schedule |
| `grouper_enable_cron_jobs` | `false` | Cron entry is created disabled by default - flip to `true` once `grouper_run_args` is set deliberately |

## Vault variables

Declared as role defaults (see `defaults/main.yml`) so consumers can see
what's expected, sourced from ansible-vault:

| Role default | Vault var |
| --- | --- |
| `grouper_staging_galaxy_api_key` | `vault_jenkins_bot_staging_api_key` |
| `grouper_prod_galaxy_api_key` | `vault_jenkins_bot_production_api_key` |
| `grouper_slack_token` | `vault_galaxy_australia_slack_api_token` |

These are templated into `{{ grouper_dir }}/.env` (mode `0600`) and read at
runtime via `python-dotenv` (`files/config.py`).

## `grouper` CLI

Run from `grouper_dir` via the venv: `python -m grouper [flags]`.

| Flag | Effect |
| --- | --- |
| `-c`, `--commit` | Act for real. Without it, every run is a dry-run: changes are listed and Slack messages are logged, not sent |
| `--add` / `--remove` | Add/remove users to/from groups based on email domain |
| `-n`, `--notify` | Post Slack messages for changes found |
| `--all` | Check every user, not just ones added/removed since the last run |
| `-l`, `--list` | List domains currently associated with each group, then exit |
| `--limit N` (default 50) | Refuse to act on more than N group-membership changes in one run |
| `--force` | Override `--limit` |
| `--production` | Act against the production Galaxy server instead of staging |
| `--grouper-dir PATH` | Override where `approved_domains.json`/`users.json`/`grouper.log` are read/written (default: alongside the installed package) |
| `-g`, `--generate` | Write the current Galaxy user id list to `users.json` without adding/removing/notifying anything |

## Approved domains

`files/approved_domains.json` maps group names to lists of email domains:

```json
{
  "AU Researchers": ["uq.edu.au"],
  "Australian_government": ["*.gov.au", "aims.gov.au"]
}
```

Most entries are **exact**: `student.uq.edu.au` does not match
`uq.edu.au` unless it's listed in its own right. An entry beginning with
`*.` is a **wildcard** and matches any domain with one or more labels
under that suffix - `health.gov.au` and `dst.defence.gov.au` both match
`*.gov.au`, but the bare suffix `gov.au` does not match its own wildcard.

**A user is assigned to every group whose rules match their email
domain.** There is no precedence between exact and wildcard entries, or
between overlapping wildcards - the result is the plain union of every
match. A domain matched by five separate rules joins five groups.

## First run

Before the first real pass, `users.json` doesn't exist, so there's nothing
for grouper to diff against. Generate it once:

```
python -m grouper --generate
```

This records every current Galaxy user as "already seen," so the next
scheduled run only reports genuinely new or deleted users rather than
treating the entire user base as new.

## Logs

`python -m grouper` logs to stdout (which `run_groups.sh` redirects to
`grouper_run_log_path`, overwritten each run) and to a rotating file,
`grouper.log`, inside `grouper_dir` (kept up to 5 x 1MB backups) - this is
the log to check for anything older than the last cron tick.

## Safety

- Every run is a dry-run unless `--commit` is passed. `grouper_run_args`
  defaults to `""`, so cron acts on nothing until it's deliberately
  changed.
- `run_groups.sh` uses `flock` so only one instance runs at a time, and
  blocks future scheduled runs (writing `.run_groups.blocked` and sending
  a Slack alert via `notify_failure.py`) if grouper exits non-zero. Remove
  the block file to resume.
- `--limit` (default 50) refuses to act on an unexpectedly large batch of
  changes - e.g. a truncated Galaxy user list or a bad edit to
  `approved_domains.json` - without `--force`, alerting Slack instead.
