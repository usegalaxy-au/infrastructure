#! /bin/bash
keep_error_days_arg = "$1"
[ "$keep_error_days_arg" ] && keep_error_days=$keep_error_days_arg || keep_error_days={{ dt_pulsar.keep_error_days }}

python {{ dt_home }}/remove_pulsar_jwds.py --pulsar_name {{ dt_pulsar.pulsar_name }} --ssh_key {{ dt_pulsar.ssh_key }} \
    --pulsar_ip_address {{ dt_pulsar.pulsar_ip_address }} {% if dt_pulsar.pulsar_staging_dir %} --pulsar_staging_dir {{ dt_pulsar.pulsar_staging_dir }}{% endif %} \
    --keep_error_days $keep_error_days {% if not dt_pulsar.delete_jwds %}--dry_run{% endif %} \

