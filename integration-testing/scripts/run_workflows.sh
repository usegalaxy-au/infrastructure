#!/bin/bash
set -ex
: ${PLANEMO_OPTIONS:=""}  # e.g. PLANEMO_OPTIONS="--verbose"

export GALAXY_URL=$1
export GALAXY_USER_KEY=$2

# Ensure we can find this history later.
nonce=$(date +%s)
history_name="$1 $nonce"

for WORKFLOW in $(ls workflows/*.ga); do

	# Run test.
	set +e # Do not die if planemo returns non-zero
	planemo $PLANEMO_OPTIONS test \
		--history_name "$history_name" \
		--galaxy_url "$GALAXY_URL" \
		--galaxy_user_key "$GALAXY_USER_KEY" \
		--no_shed_install \
		--engine external_galaxy \
		"$WORKFLOW";
	planemo_exit_code=$?
	set -e

done

exit $planemo_exit_code