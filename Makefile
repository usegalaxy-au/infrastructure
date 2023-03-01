# Management commands

KEY_FILE = ~/.ssh/galaxy  # symlink this if your filename is different

install-roles:
	ansible-galaxy install -p roles -r requirements.yml

update-roles:
	python scripts/update_roles.py

run-dev:
	ansible-playbook -i hosts --key-file $(KEY_FILE) dev_playbook.yml

run-staging:
	ansible-playbook -i hosts --key-file $(KEY_FILE) staging_playbook.yml

run-prod:
	ansible-playbook -i hosts --key-file $(KEY_FILE) aarnet_playbook.yml
