source jenkins/utils.sh

# check whether the production tpv files have changed
PROD_TPV_FILE_PATH="files/galaxy/dynamic_job_rules/production/total_perspective_vortex"
PROD_TPV_UPDATED=$(git diff --name-only $GIT_PREVIOUS_COMMIT $GIT_COMMIT | cat | grep $PROD_TPV_FILE_PATH)

# check whether dev files of interest have changed
DEV_LOCAL_TOOL_CONF="files/galaxy/config/local_tool_conf_dev.xml"
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

activate_virtualenv
echo "helloworld" > .vault_pass.txt  # ansible needs .vault_pass.txt to exist

if [ "$PROD_TPV_UPDATED" ]; then
    echo -e "\nUpdating tool destinations file on Galaxy production instance\n"

    ansible-playbook -i hosts aarnet_update_configs_playbook.yml --extra-vars "ansible_user=jenkins_bot" --vault-password-file "$VAULT_PASS"
fi

if [ "$DEV_RELEVANT_FILES_UPDATED" ]; then
    echo -e "\nUpdating tool destinations file on Galaxy dev instance\n"

    ansible-playbook -i hosts dev_update_configs_playbook.yml --extra-vars "ansible_user=jenkins_bot" --vault-password-file "$VAULT_PASS"
fi

if [ "$STAGING_RELEVANT_FILES_UPDATED" ]; then
    echo -e "\nUpdating tool destinations file on Galaxy staging instance\n"

    ansible-playbook -i hosts staging_update_configs_playbook.yml --extra-vars "ansible_user=jenkins_bot" --vault-password-file "$VAULT_PASS"
fi

