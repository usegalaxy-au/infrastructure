source jenkins/utils.sh

export VENV_NAME=.check_data_tables_venv
export REQUIREMENTS_FILE="jenkins/check_data_tables/requirements.txt"

activate_virtualenv

python jenkins/check_data_tables/check_data_tables_for_dups.py -a $API_KEY --notify --slack_token $SLACK_TOKEN
