#!/usr/bin/env python
# Author: Helena Rasche
# License: AGPL-3.0
import json
import requests
import yaml
import subprocess


with open('requirements.yml', 'r') as handle:
    desired = yaml.safe_load(handle)

for role in desired:
    if '://' in role.get('src', role.get('name')):
        continue

    if '.' not in role.get('version', ''):
        continue

    role_info = subprocess.check_output(['ansible-galaxy', 'role', 'info', role.get('src', role.get('name'))]).decode('utf-8')
    role_id = [x[x.index(':') + 2:].strip() for x in role_info.split('\n') if '\tid:' in x][0]
    data = requests.get('https://galaxy.ansible.com/api/v1/roles/' + role_id + '/?format=json').json()
    try:
        oldv = role['version']
        newv = data['summary_fields']['versions'][0]['name']
        if oldv != newv:
            print(f"{role.get('src', role.get('name')):<25s} {oldv} → {newv}")
    except:
        print(f"Error processing {role['src']}")
