#! /bin/bash

source jenkins/utils.sh

activate_virtualenv
echo "secret" > .vault_pass.txt  # ansible needs .vault_pass.txt to exist

ansible-playbook -i hosts jenkins/phone_in_utils/restart_galaxy_handlers_playbook.yml
