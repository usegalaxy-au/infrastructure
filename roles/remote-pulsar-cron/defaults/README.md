## remote-pulsar-cron role

Ansible role for making job queries on the galaxy machine and removing job working directories on remote pulsar machines

**Author: Catherine Bromhead 2021**

### Prerequisites

Ubuntu operating system
ssh key(s) belonging to the nominated user with mode 0400

### Role Variables

**rpc_user** The user who owns the files on galaxy and runs the cron jobs
**rpc_home** Directory on galaxy where scripts live
default: /home/<rpc_user>/remote_pulsar_cron
**rpc_remote_user** A superuser on remote pulsars
**rpc_pulsar_staging_dir** The staging directory on pulsar machines where the job working directories are.  This can be set for each machine in rpc_pulsar_servers.

**rpc_pulsar_servers** A list of dicts with the following keys
*pulsar_name*
*pulsar_ip_address*
*ssh_key* (path to ssh key on galaxy that will give the rpc_user access to the remote pulsar)
*delete_jwds* (boolean, actually delete the remote job working directories identified for deletion.  default: false)
*keep_error_days* (an integer number of days to keep jobs that finished in error state)
*cron_hour* (for cron job with respect to system time on galaxy)
*cron_minute* (as above)
*pulsar_staging_dir* (defaults to rpc_pulsar_staging_dir)

example:

```
rpc_pulsar_machines:
  - pulsar_name: pulsar-catherine
    pulsar_ip_address: "{{ hostvars['pulsar-catherine']['ansible_ssh_host'] }}"
    ssh_key: /home/ubuntu/.ssh/key
    delete_jwds: true
    keep_error_days: 4
    cron_hour: "17"
    cron_minute: "00"
  - pulsar_name: pulsar-helen
    pulsar_ip_address: "{{ hostvars['pulsar-helen']['ansible_ssh_host'] }}"
    ssh_key: /home/ubuntu/.ssh/key
    delete_jwds: true
    keep_error_days: 7
    cron_hour: "17"
    cron_minute: "10"
```

