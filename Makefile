# Management commands


# This 'make' hack allows us to accept a single positional argument for the
# 'run' target:
# -----------------------------------------------------------------------------
# If the first argument is "run"...
ifeq (run,$(firstword $(MAKECMDGOALS)))
  # get the second argument for "run"
  PLAYBOOK := $(wordlist 2, 2, $(MAKECMDGOALS))
  # ...and turn it into do-nothing target
  $(eval $(PLAYBOOK):;@:)
  $(info RUN PLAYBOOK ${PLAYBOOK}_playbook.yml)
endif
# -----------------------------------------------------------------------------


KEY_FILE?=~/.ssh/galaxy  # set env var KEY_FILE to override this (or symlink your key)


# Generic entrypoint for all playbooks e.g. $ make run dev -> dev_playbook.yml
run:
	ansible-playbook -i hosts --key-file $(KEY_FILE) $(PLAYBOOK)_playbook.yml

install-roles:
	ansible-galaxy install -p roles -r requirements.yml

install-requirements:
	ansible-galaxy install -r requirements.yml

force-install-requirements:
	ansible-galaxy install -r requirements.yml -f

update-roles:
	python scripts/update_roles.py

ansible-find-upgrades:
	python scripts/ansible-find-upgrades.py
	
