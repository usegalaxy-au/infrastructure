# Activate the virtual environment on jenkins. If this script is being run for
# the first time we will need to set up the virtual environment
VIRTUALENV="../.ansible_venv"
REQUIREMENTS_FILE="jenkins/requirements.txt"
CACHED_REQUIREMENTS_FILE="$VIRTUALENV/cached_requirements.txt"

[ ! -d $VIRTUALENV ] && virtualenv -p python3 $VIRTUALENV
# shellcheck source=../.venv3/bin/activate
. "$VIRTUALENV/bin/activate"

# if requirements change, reinstall requirements
[ ! -f $CACHED_REQUIREMENTS_FILE ] && touch $CACHED_REQUIREMENTS_FILE
if [ "$(diff $REQUIREMENTS_FILE $CACHED_REQUIREMENTS_FILE)" ]; then
pip install -r $REQUIREMENTS_FILE
cp $REQUIREMENTS_FILE $CACHED_REQUIREMENTS_FILE
fi

echo "secret" > .vault_pass.txt  # ansible needs .vault_pass.txt to exist
ansible-playbook -i hosts jenkins/update_labels/update_tool_labels_playbook.yml --extra-vars "ansible_user=jenkins_bot update_labels_hostname=staging_galaxy_server"

# leave commented out until after this has been run on staging a couple of times
# ansible-playbook -i hosts jenkins/update_labels/update_tool_labels_playbook.yml --extra-vars "ansible_user=jenkins_bot update_labels_hostname=pawsey_galaxy_server"