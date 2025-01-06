source jenkins/utils.sh

export VENV_NAME=.check_data_tables_venv
export REQUIREMENTS_FILE="jenkins/check_data_tables/requirements.txt"

activate_virtualenv

python check_data_table_for_duplicates.py -a $API_KEY --notify --slack_token $SLACK_TOKEN
