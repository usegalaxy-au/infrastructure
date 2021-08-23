wget https://raw.githubusercontent.com/galaxyproject/galaxy/release_20.05/lib/galaxy/jobs/dynamic_tool_destination.py

[ "$SETTING" = "github" ] && rm ansible.cfg # ansible will protest about lack of vault password file and refuse to run otherwise.  this change is not committed
ansible all -i localhost, -c local -m template -a "src=templates/galaxy/config/job_conf.xml.j2 dest=job_conf.xml" --extra-vars=@host_vars/aarnet_job_conf.yml --extra-vars=@.ci/test_vars/job_conf_test_vars.yml

echo -e "\nRunning job destination check\n"
SUCCESS_RESPONSE="Configuration is valid!"
VALIDATION_OUTPUT="$(python dynamic_tool_destination.py -c files/galaxy/dynamic_job_rules/aarnet/dynamic_rules/tool_destinations.yml -j job_conf.xml)"
echo -e "$VALIDATION_OUTPUT"

rm job_conf.xml
rm dynamic_tool_destination.py

if [[ "$VALIDATION_OUTPUT" == *"$SUCCESS_RESPONSE"* ]]; then
  exit 0
else
  exit 1
fi