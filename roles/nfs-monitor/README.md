# nfs-monitor

An Ansible role that installs a lightweight NFS watchdog. The role drops a small Python utility that tails the kernel journal for `nfs: server ... not responding/OK` messages, stores the last seen state, and posts transitions to a Slack channel so the team can be aware of timeouts.

## What gets installed

* Creates `{{ nfs_monitor_dir }}` with `logs/` and `state/` subdirectories, owned by `{{ nfs_monitor_user }}`.
* Renders `config.yml` from `templates/config.yml.j2`, which passes Slack credentials, sender label, and the list of servers to the monitor.
* Copies `monitor.py` plus its `requirements.txt`, installs dependencies into `{{ nfs_monitor_virtualenv_path }}`, and wires a cron job that runs on the schedule defined by `nfs_monitor_cron_*`.
* Cron runs `monitor.py --config ...`. The script shells out to `sudo journalctl -k --since "10 minutes ago"` to parse the most recent kernel log entries, debounces flapping alerts, logs to `logs/events.log`, and tracks per-server state files under `state/`.

## Requirements

* Python 3 with `pip` on the remote host (the role creates a dedicated virtualenv).
* Ability for `{{ nfs_monitor_user }}` to run `sudo journalctl -k ...` without interaction, otherwise cron will fail.
* An incoming Slack token that is allowed to post to the configured channel.

## Role variables

All variables live in `defaults/main.yml`.

| Variable | Description | Default |
| --- | --- | --- |
| `nfs_monitor_slack_channel` | Channel to post to (required). | _unset_ |
| `nfs_monitor_slack_token` | Bot/user token with `chat:write`. | _unset_ |
| `nfs_monitor_servers` | List of dicts (`identifier`, `name`). Identifier must match the value printed in kernel logs (hostname/IP). | _unset_ |
| `nfs_monitor_sender` | Friendly label shown in Slack messages. | `{{ ansible_hostname }}` |
| `nfs_monitor_user` | Unix user who owns files and runs cron. | `ubuntu` |
| `nfs_monitor_dir` | Install root for the monitor and its config/assets. | `/home/{{ nfs_monitor_user }}/nfs_monitor` |
| `nfs_monitor_virtualenv_path` | Where to create the virtualenv used by cron. | `{{ nfs_monitor_dir }}/venv` |
| `nfs_monitor_python` | Interpreter used for virtualenv creation. | `/usr/bin/python3` |
| `nfs_monitor_debounce_minutes` | Suppress Slack if a server flaps back within this window. | `0` |
| `nfs_monitor_cron_enabled` | Toggle the cron job. | `true` |
| `nfs_monitor_cron_minute`..`weekday` | Standard Ansible cron schedule knobs. | `*/2 * * * *` |

Set the first three variables explicitly; they are commented out in defaults but must be provided via inventory/group vars or a vault.

## Example

```yaml
# inventory/group_vars/nfs.yml
nfs_monitor_slack_channel: "#alerts"
nfs_monitor_slack_token: "{{ vault_nfs_monitor_slack_token }}"
nfs_monitor_servers:
  - identifier: "galaxy-aust-exports@genome.edu.au"
    name: "galaxy-aust-exports"
  - identifier: "192.168.205.249"
    name: "galaxy-user-nfs"
nfs_monitor_debounce_minutes: 5
nfs_monitor_cron_minute: "*/1"
```

```yaml
# playbook.yml
- hosts: nfs_monitor_nodes
  roles:
    - role: nfs-monitor
```

Run the playbook and check `/home/<user>/nfs_monitor/logs/events.log` or execute `monitor.py --config ... --dry-run` manually if you want to validate alerts without pinging Slack.
