#! /bin/bash
keep_error_days_arg = "$1"
[ "$keep_error_days_arg" ] && keep_error_days=$keep_error_days_arg || keep_error_days={{ keep_error_days }}

python {{ rpc_home }}/remove_pulsar_jwds.py --pulsar_name {{ pulsar_name }} --ssh_key {{ssh_key }} \
    --pulsar_ip_address {{ pulsar_ip_address }} --pulsar_staging_dir {{ pulsar_staging_dir }} \
    --keep_error_days $keep_error_days_arg {% if dry_run %}--dry_run{% endif %}

