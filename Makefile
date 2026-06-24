# Management commands

# This 'make' hack allows us to accept a single positional argument for the 'run' target:
# -----------------------------------------------------------------------------
# If the first argument is "run"...
ifeq (run,$(firstword $(MAKECMDGOALS)))
  # Get the second argument for "run"
  PLAYBOOK := $(wordlist 2, 2, $(MAKECMDGOALS))

  # Get additional arguments after the playbook name (everything else)
  EXTRA_ARGS := $(wordlist 3, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))

  # Prevent make from interpreting arguments as its own options
  MAKEFLAGS += --silent

  # Turn extra args into do-nothing targets
  $(eval $(PLAYBOOK):;@:)
  $(foreach arg,$(EXTRA_ARGS),$(eval $(arg):;@:))

  $(info RUN PLAYBOOK ${PLAYBOOK}_playbook.yml)
  $(info EXTRA ARGS: ${EXTRA_ARGS})
endif
# -----------------------------------------------------------------------------

KEY_FILE?=~/.ssh/galaxy  # set env var KEY_FILE to override this (or symlink your key)

# Generic entrypoint for all playbooks e.g. $ make run dev -> dev_playbook.yml
run:
	ansible-playbook -i hosts --key-file $(KEY_FILE) $(PLAYBOOK)_playbook.yml $(EXTRA_ARGS)

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
	
