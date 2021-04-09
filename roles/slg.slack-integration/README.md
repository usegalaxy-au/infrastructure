# Monitoring Slack Integration Role

Ansible role for setting up basic machine monitoring (via cron) which reports to a Slack channel. Used in Galaxy Australia for alerts on disk use, mount status, machine loads and CVMFS connectivity.

**Author: Simon Gladman 2021**

Based on a series of shell scripts written by Tinker (Thom Cuddihy - https://github.com/thomcuddihy). Uses Thom's monitoring bash script he wrote for GA and his Slack integration tools from github.

## Pre-requisites

git

## Role Variables

### Path Variables

**ga_watch_install_path**

The path to install the monitoring script to on the taerget machines. Default: `/root/tools`

**slacktools_git**
URL to download Thom Cuddihy's slack tools Default: `"https://github.com/thomcuddihy/slack_tools"`

**slacktools_path**

Install path for slack tools. Default: `"/root/tools/slack_tools"`

### Slack variables

**slack_token**

The Slack authentication token - must be set in Slack. Preferably stored in an encrypted vault.

**slack_channel**

The Slack channel to send the notifications to. Default: `"#alerts"`

**slack_mentions**

A comma delimited list of users to mention in the posts. Add them in the form of "@joe". Default: `""`

### Watch toggles

This is a list of variables that can be overridden to toggle on/off various things to watch. e.g. root/sudo user logins, loads, mounts etc. Names are self explanatory.

**watch_users**

When set to true, will monitor and report on sudo/root user logins. Default: `false`

**watch_loads**

When set to true, will monitor and report on machine loads. Uses a normal/high threshold. Default: `false`

**watch_mounts**

When set to true, will monitor and report on mount connectivity. Uses list of mounts returned by `mount` command filtered to remove devices in `/dev` and temporary dirs. Default: `false`

**watch_cvmfs**

When set to true, will monitor and report on CVMFS connectivity. Default: `false`

**watch_diskuse**

When set to true, will monitor and report on local disk use. Reports > 75% and > 90%. Default: `false`

**watch_slurm**

Not yet implemented. When done will report on slurm status. Default: `false`

### Timing

**ga_watch_check_time**

Will run the script this often (in minutes.) Default: `5`

## Example playbook

```yaml
- hosts: cvmfs_clients
  vars:
    slack_token: "fhsopfuergpegjherotjhgoihwefoiighsdoflewkhjrgohjvg"
    watch_loads: true
    watch_users: true
    watch_cvmfs: true
  roles:
    - role: slg.slack-integration
```      