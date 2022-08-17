source jenkins/utils.sh

activate_virtualenv
echo "secret" > .vault_pass.txt  # ansible needs .vault_pass.txt to exist

ansible-playbook -i hosts jenkins/update_labels/update_tool_labels_playbook.yml --extra-vars "ansible_user=jenkins_bot update_labels_hostname=staging_galaxy_server"

ansible-playbook -i hosts jenkins/update_labels/update_tool_labels_playbook.yml --extra-vars "ansible_user=jenkins_bot update_labels_hostname=aarnet_galaxy_server"