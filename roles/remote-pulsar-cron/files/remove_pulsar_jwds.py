import argparse
import datetime
import os
import subprocess

"""
Script to delete pulsar job working directories from galaxy.  It logs into a pulsar server and gets the names
of job working directories stored there and runs queries to find which of these can be deleted.  All job working
directories for jobs in 'ok' and 'deleted' states can go.  Job working directories in state 'error' can be kept
for a number of days supplied as the `keep_error_days` argument.  It is run from galaxy because of rules that
prevent remote users from running sql commands.
"""

pulsar_staging_dir = '/mnt/pulsar/files/staging'
log_of_everything = 'remove_jwds_log'


def sanitize_subprocess_output_list(command):
    blob = subprocess.check_output(command, shell=True)
    return blob.decode('utf-8').replace('\n', ' ').strip().split()


def is_job_id(id):
    try:
        job_num = int(id)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description='Write a script to remove job working dirs that can be removed on pulsar')
    parser.add_argument('--pulsar_name', required=False, help='Human understandable name for pulsar, i.e. pulsar-mel5')
    parser.add_argument('--pulsar_ip_address', help='IP address of remote pulsar')
    parser.add_argument('--ssh_key', help='Absolute path to ssh key on local machine')
    parser.add_argument('-e', '--keep_error_days', type=int, default=None, help='Keep error state job working directories completed within `keep_error_days` days')
    parser.add_argument('--dry_run', action='store_true', help='Do not the delete script on the remote pulsar')  # flag name copied from gxadmin
    args = parser.parse_args()

    ssh_key = args.ssh_key
    if not os.path.exists(ssh_key):
        raise Exception(f'SSH key not found: {ssh_key}')
    keep_error_days = args.keep_error_days
    pulsar_ip = args.pulsar_ip_address
    pulsar_name = arg.pulsar_name if args.pulsar_name else args.pulsar_ip_address
    rm_jwds_script = f'rm_jwds_{pulsar_name}.sh'

    job_ids = sanitize_subprocess_output_list(f'ssh -i {ssh_key} ubuntu@{pulsar_ip} \"ls {pulsar_staging_dir}\"')
    job_ids = [jid for jid in job_ids if is_job_id(jid)] # filter out anything that may not be a job working directory

    def get_job_query(state, save_days=None):
        query = f'psql -t -c \"select j.id from job j where j.state = \'{state}\' and j.id in ({", ".join(job_ids)})'
        if save_days:
            query += f' and j.update_time < current_date - interval \'{save_days}\' day'
        query += '\";'
        return query

    ok_job_ids = sanitize_subprocess_output_list(get_job_query(state='ok'))
    deleted_job_ids = sanitize_subprocess_output_list(get_job_query(state='deleted'))
    if args.keep_error_days: # otherwise keep all error jobs
        error_job_ids = sanitize_subprocess_output_list(get_job_query(state='error', save_days = args.keep_error_days))
    else:
        error_job_ids = []

    with open(rm_jwds_script, 'w') as handle:
        handle.write('# ok jobs\n')
        for id in ok_job_ids:
            handle.write(f'rm -rf {id}\n')
        handle.write('# deleted jobs\n')
        for id in deleted_job_ids:
            handle.write(f'rm -rf {id}\n')
        if error_job_ids:
            handle.write(f'# error jobs more than {args.keep_error_days} old\n')
            for id in error_job_ids:
                handle.write(f'rm -rf {id}\n')

     # keep a record of everything we have deleted and when
    job_query_result = subprocess.check_output(
        f'psql -c \"select j.id, j.state, j.update_time, j.destination_id from job j where j.id in ({", ".join(ok_job_ids + deleted_job_ids + error_job_ids)});\"',
        shell=True,
    ).decode('utf-8')

    with open(log_of_everything, 'a+') as log_handle:
        date_time = datetime.datetime().strftime('%Y%m%d_%H.%M.%S')
        dry_run = ' [dry run]' if args.dry_run else ''
        log_handle.write(f'Running delete jwds script for {pulsar_name} keep_error_days {keep_error_days} {date_time} {dry_run}\n')
        log_handle.write(job_query_result)
        log_handle.write('\n')

        log_handle.write('Copying script to remote pulsar\n')
        copy_exit_code = subprocess.call(f'scp -i {ssh_key} {rm_jwds_script} ubuntu@{pulsar_ip}:{pulsar_staging_dir}', shell=True)
        if not copy_exit_code == 0:
            log_handle.write('Error: Failed to copy {rm_jwds_script}\n\n')
        if not args.dry_run:
        script_exit_code = subprocess.call(f'ssh -i {ssh_key} ubuntu@{pulsar_ip} \"cd {pulsar_staging_dir}; sudo bash {rm_jwds_script}\"', shell=True)

        the_time = datetime.datetime().strftime('%Y%m%d %H:%M:%S')
        log_handle.write('{the_time}: Finished running script with exit code {exit_code}\n\n')


if __name__ == '__main__':
    main()