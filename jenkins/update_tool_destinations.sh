# check whether the production tpv files have changed
PROD_TPV_FILE_PATH="files/galaxy/dynamic_job_rules/pawsey/total_perspective_vortex"
PROD_TPV_UPDATED=$(git diff --name-only $GIT_PREVIOUS_COMMIT $GIT_COMMIT | cat | grep $PROD_TPV_FILE_PATH)

# check whether dev files of interest have changed
DEV_LOCAL_TOOL_CONF="files/config/local_tool_conf_dev.xml"
DEV_JOB_CONF_PATH="templates/galaxy/config/dev_job_conf.yml.j2"
DEV_TPV_FILE_PATH="files/galaxy/dynamic_job_rules/dev/total_perspective_vortex"
DEV_RELEVANT_FILES_UPDATED=$(git diff --name-only $GIT_PREVIOUS_COMMIT $GIT_COMMIT | cat | grep -E "$DEV_TPV_FILE_PATH|$DEV_JOB_CONF_PATH|$DEV_LOCAL_TOOL_CONF")

# check staging files
STAGING_JOB_CONF_PATH="templates/galaxy/config/staging_job_conf.yml.j2"
STAGING_TPV_FILE_PATH="files/galaxy/dynamic_job_rules/staging/total_perspective_vortex"
STAGING_RELEVANT_FILES_UPDATED=$(git diff --name-only $GIT_PREVIOUS_COMMIT $GIT_COMMIT | cat | grep -E "$STAGING_TPV_FILE_PATH|$STAGING_JOB_CONF_PATH")


if [ ! "$PROD_TPV_UPDATED" ] && [ ! "$DEV_RELEVANT_FILES_UPDATED" ] && [ ! "$STAGING_RELEVANT_FILES_UPDATED" ]; then
    # nothing to do
    echo -e "\nNo updates to tool destinations\n"
    exit 0
fi

# Activate the virtual environment on jenkins. If this script is being run for
# the first time we will need to set up the virtual environment
VIRTUALENV="../.ansible_venv"
REQUIREMENTS_FILE="jenkins/requirements.txt"
CACHED_REQUIREMENTS_FILE="$VIRTUALENV/cached_requirements.txt"
echo "helloworld" > .vault_pass.txt  # ansible needs .vault_pass.txt to exist

[ ! -d $VIRTUALENV ] && virtualenv -p python3 $VIRTUALENV
# shellcheck source=../.venv3/bin/activate
. "$VIRTUALENV/bin/activate"

# if requirements change, reinstall requirements
[ ! -f $CACHED_REQUIREMENTS_FILE ] && touch $CACHED_REQUIREMENTS_FILE
if [ "$(diff $REQUIREMENTS_FILE $CACHED_REQUIREMENTS_FILE)" ]; then
pip install -r $REQUIREMENTS_FILE
cp $REQUIREMENTS_FILE $CACHED_REQUIREMENTS_FILE
fi

if [ "$PROD_TPV_UPDATED" ]; then
    echo -e "\nUpdating tool destinations file on Galaxy production instance\n"

    ansible-playbook -i hosts pawsey_update_job_conf_playbook.yml --extra-vars "ansible_user=jenkins_bot" --vault-password-file "$VAULT_PASS"
fi

if [ "$DEV_RELEVANT_FILES_UPDATED" ]; then
    echo -e "\nUpdating tool destinations file on Galaxy dev instance\n"

    ansible-playbook -i hosts dev_update_configs_playbook.yml --extra-vars "ansible_user=jenkins_bot" --vault-password-file "$VAULT_PASS"
fi

if [ "$STAGING_RELEVANT_FILES_UPDATED" ]; then
    echo -e "\nUpdating tool destinations file on Galaxy staging instance\n"

    ansible-playbook -i hosts staging_update_configs_playbook.yml --extra-vars "ansible_user=jenkins_bot" --vault-password-file "$VAULT_PASS"
fi

