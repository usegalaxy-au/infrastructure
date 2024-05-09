import subprocess
import argparse
import re
import os
import yaml

MINUTES_IN_DAY=1440
MINUTES_IN_HOUR=60

squeue_format="%8i %.50j %.9T %.12M %.40N" # slurm_id, name, state, runtime, node

vars_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clean_tmpdisk_variables.yml')

with open(vars_file) as handle:
    vars = yaml.safe_load(handle)
    worker_node = vars['worker_node']
    tmp_dir = vars['tmp_dir']

# integrity check for tmp_dir variable:
accepted_tmp_dirs = ['/tmp', '/mnt/tmpdisk']
if not tmp_dir in accepted_tmp_dirs: # safety feature to stop this from accidentally being set to something we don't want
    raise Exception(f'specified clean_tmpdisk_tmp_dir must be one of {str(accepted_tmp_dirs)}')

def to_minutes(slurm_time):
    pattern_dhms = re.compile('(?P<days>\d+)-(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)')
    pattern_hms = re.compile('(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)')
    match = re.match(pattern_dhms, slurm_time)
    if not match:
        match = re.match(pattern_hms, slurm_time)
    values = {}
    for val in ['days', 'hours', 'minutes']:
        values[val] = int(match.groupdict().get(val)) if match.groupdict().get(val) else 0
    minutes = MINUTES_IN_DAY * values['days'] + MINUTES_IN_HOUR * values['hours'] + values['minutes'] + 1
    return minutes

def main():
    parser  = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry_run', action='store_true', help="Print but do not execute command")
    parser.add_argument('-l', '--list_only', action='store_true', help="List files to remove (but do not remove them)")
    parser.add_argument('-v', '--verbose', action='store_true', help="Be verbose")
    args = parser.parse_args()

    list_only = args.list_only
    dry_run = args.dry_run or args.list_only # enforce dry run in the case of printing the list
    verbose = args.verbose

    squeue_details = subprocess.check_output(f'squeue --format=\'{squeue_format}\' --states=RUNNING -w {worker_node}', shell=True)

    squeue_details = squeue_details.decode('utf-8')

    if verbose:
        print("Squeue output:\n")
        print(squeue_details)

    squeue_details_rows = squeue_details.split('\n')[1:]
    jobs = []
    for row in squeue_details_rows:
        if not row.strip():
            continue
        slurm_id, name, state, runtime, node = re.split('\s+', row.strip())
        if node != worker_node:
            continue
        job = {
            'slurm_id': slurm_id,
            'name': name,
            'state': state,
            'runtime_minutes': to_minutes(runtime),
            'node': node,
        }
        jobs.append(job)

    if verbose:
        print('\nJobs dict:\n')
        for job in jobs:
            print(job)

    max_job_time = sorted(jobs, key=lambda x: x['runtime_minutes'], reverse=True)[0]['runtime_minutes'] if jobs else 0

    delete_files_command = f"sudo find {tmp_dir} -type f -mmin +{max_job_time + 30} -exec rm {{}} \;"

    if list_only:
        list_command = f'sudo find {tmp_dir} -type f -mmin +{max_job_time + 30} -printf "%p   %TY-%Tm-%Td\n"'
        print(f'\nFiles to delete:\n')
        file_list = subprocess.check_output(list_command, shell=True)
        file_list = file_list.decode('utf-8')
        print(file_list)

    if dry_run or verbose:
        print(f'\nCommand to run to remove files from dir {tmp_dir} last modified more than {max_job_time + 30} minutes ago')
        print(delete_files_command)
    
    if not dry_run:
        subprocess.check_output(delete_files_command, shell=True)


if __name__ == '__main__':
    main()
