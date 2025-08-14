#! /bin/bash

source jenkins/utils.sh

activate_virtualenv
echo "secret" > .vault_pass.txt  # ansible needs .vault_pass.txt to exist

ansible-playbook -i hosts galaxy_update_configs_playbook.yml --extra-vars "ansible_user=jenkins_bot jenkins_exec=True" --vault-password-file "$VAULT_PASS"
