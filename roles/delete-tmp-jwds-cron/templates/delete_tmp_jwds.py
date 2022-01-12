import argparse
import datetime
import os
import subprocess

global_keep_error_days = {{ dt_tmp_jwd_keep_error_days }}
connection_string = '{{ dt_connection_string }}'
jwd_base = '{{ dt_jwd_base }}'
remote_user = '{{ dt_remote_user }}'
remote_ip = '{{ dt_remote_ip }}'
ssh_key = '{{ dt_ssh_key }}'
global_dry_run = True  # meaning the script be created but not run for the moment

bash_script_name = 'rm_tmp_jwds.sh'
log_file_name = 'log.txt'
dirname = os.path.dirname(__file__)
rm_tmp_jwds_script = os.path.join(dirname, bash_script_name)
log_file = os.path.join(dirname, log_file_name)

def main():
    parser = argparse.ArgumentParser(description='Remove older job working directories in error state from the tmp disk')
    parser.add_argument(
        '-e', '--keep_error_days', type=int, default=global_keep_error_days,
        help='Keep error state job working directories completed within `keep_error_days` days'
    )
    parser.add_argument('--dry_run', action='store_true', help='Do not run the delete script')
    parser.add_argument('-c', '--check', action='store_true', help='Print details of jwds to screen')
    args = parser.parse_args()
    keep_error_days = args.keep_error_days
    dry_run = args.dry_run or global_dry_run
    check = args.check

    jwds = []

    # Assume a directory structure where each jwd's path looks like 001/225/1225800 and job ids with at least 7 digits
    job_dirs_level_1 = [d for d in os.listdir(jwd_base) if os.path.isdir(os.path.join(jwd_base, d)) and len(d) == 3 and is_string_int(d)]
    for dir1 in sorted(job_dirs_level_1, key=lambda x: int(x)):
        job_dirs_level_2 = [d for d in os.listdir(os.path.join(jwd_base, dir1)) if os.path.isdir(os.path.join(jwd_base, dir1, d)) and len(d) == 3 and is_string_int(d)]
        for dir2 in sorted(job_dirs_level_2, key=lambda x: int(x)):
            job_dirs = [d for d in os.listdir(os.path.join(jwd_base, dir1, dir2)) if is_string_int(d) and len(d) >= 7 and os.path.isdir(os.path.join(jwd_base, dir1, dir2, d))]
            for job_dir in job_dirs:
                jwds.append({'id': job_dir, 'path': os.path.join(jwd_base, dir1, dir2, job_dir)})

    jwd_ids_to_delete = []
    intervals = get_intervals(len(jwds))  # run queries batches because the list is too long for subprocess
    for interval in intervals:
        jwd_batch = jwds[interval['begin']:interval['end']]
        batch_ids_to_delete = sanitize_subprocess_output_list(get_job_query(job_ids=[jwd['id'] for jwd in jwd_batch], keep_error_days=keep_error_days))
        jwd_ids_to_delete.extend(batch_ids_to_delete)

    jwds_to_delete = [jwd for jwd in jwds if jwd['id'] in jwd_ids_to_delete]

    with open(rm_tmp_jwds_script, 'w') as handle:
        handle.write('#!/bin/bash\n\n')
        for jwd in jwds_to_delete:
            handle.write(f'rm -rf {jwd["path"]}\n')

    job_query_result = ''
    intervals = get_intervals(len(jwds_to_delete))
    for interval in intervals:
        jwds_for_deletion_batch = jwds_to_delete[interval['begin']:interval['end']]
        job_query_result_section = subprocess.check_output(
            f'psql -d {connection_string} -c \"select j.id, j.state, j.update_time from job j where j.id in ({", ".join([j["id"] for j in jwds_for_deletion_batch])});\"',
            shell=True,
        ).decode('utf-8')
        job_query_result += job_query_result_section

    if check:
        print(job_query_result)
    
    with open(log_file, 'a+') as log_handle:
        dry_run = ' [dry run]' if dry_run else ''
        log_handle.write(f'{get_current_time()}: Running delete tmp jwds script, keep_error_days={keep_error_days}{dry_run}\n')
        log_handle.write(job_query_result)
        copy_exit_code = subprocess.call(f'scp -i {ssh_key} -o StrictHostKeyChecking=no {rm_tmp_jwds_script} {remote_user}@{remote_ip}:/home/{remote_user}', shell=True)
        if not copy_exit_code == 0:
            log_handle.write(f'Error: Failed to copy {rm_tmp_jwds_script}\n\n')
            return
        if not dry_run:
            script_exit_code = subprocess.call(f'ssh -i {ssh_key} -o StrictHostKeyChecking=no {remote_user}@{remote_ip} \"sudo bash {os.path.basename(rm_tmp_jwds_script)}\"', shell=True)
            log_handle.write(f'{get_current_time()}: Finished running script with exit code {script_exit_code}\n\n')


def is_string_int(str):
    try:
        num = int(str)
        return True
    except Exception:
        return False


def sanitize_subprocess_output_list(command):
    blob = subprocess.check_output(command, shell=True)
    return blob.decode('utf-8').replace('\n', ' ').strip().split()


def get_job_query(job_ids, keep_error_days):
    state = 'error'
    query = f'psql -t -d {connection_string} -c \"select j.id from job j where j.state = \'{state}\' and j.id in ({", ".join(job_ids)})'
    query += f' and j.update_time < current_date - interval \'{keep_error_days}\' day'
    query += '\";'
    return query


def get_current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_intervals(list_length, batch_size=500):  # define batch beginnings and ends to get batches out of a list without using 'while'
    intervals = []
    beginnings = [x for x in range(list_length) if x % batch_size == 0]
    for b in beginnings:
        intervals.append({'begin': b, 'end': b + batch_size})
    intervals[-1]['end'] = list_length
    return intervals


if __name__ == '__main__':
    main()
