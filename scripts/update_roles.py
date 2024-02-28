import yaml
import re
import os
import sys
import subprocess

"""
To be run from infrastructure root directory
`python scripts/update_roles.py`

Checks elements of requirements.yml against directories in 'roles' and makes a list
of the roles with updated requirements.

Calls ansible-galaxy install -p roles -r requirements_updated.yml --force
where requirements_updated.yml contains only the roles that need to be force-installed

Note that this does not update collections, only the roles
"""

roles_to_update = []

here = os.getcwd()
roles_dir = 'roles'

if not roles_dir in os.listdir(here):
    raise Exception(f'No roles found in {roles_dir}')
output_file = 'requirements_updated.yml'

with open('requirements.yml') as handle:
    role_requirements = yaml.safe_load(handle).get('roles')

for r in role_requirements:
        name = r.get('name', r.get('src'))
        if not name:
            raise Exception(f'Could not find role {name} in yaml entry')
        required_version = r.get('version')
        if not required_version:
            print(f'role {name} has no required version, no need to update')
            continue

        role_info_file = os.path.join(here, roles_dir, name, 'meta', '.galaxy_install_info')
        if not os.path.exists(role_info_file):
            print(f'role {name} has no .galaxy_install_info, assuming new and adding to roles to install')
            roles_to_update.append(r)
        else:
            role_info_version = None
            with open(role_info_file) as handle:
                role_info_lines = handle.readlines()
            for line in role_info_lines:
                content = re.split(':\s+', line.strip())
                if content[0] == 'version':
                    role_info_version = content[1]
            if role_info_version and role_info_version == required_version:
                print(f'role {name} is already installed at version {role_info_version}, no need to update')
            else:
                print(f'role {name} will be updated from {role_info_version} to {required_version}')
                roles_to_update.append(r)
if roles_to_update:
    with open(output_file, 'w') as handle:
        yaml.safe_dump(roles_to_update, handle)
    o = subprocess.check_output([
        'ansible-galaxy',
        'install',
        '-p',
        'roles',
        '-r',
        output_file,
        '--force',
    ])
    print('\n' + '\n'.join(o.decode('utf8').split('\n')))
    os.remove(output_file)
else:
    print('No updates necessary')
