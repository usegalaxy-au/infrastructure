#!/bin/bash

galaxy_server=$1
api_key=$2


set -euo pipefail

if [ -d venv ]; then
    . venv/bin/activate
else
    bash make_environment.sh
    . venv/bin/activate
fi

shed-tools install -t tools/all_tools.yml -g $galaxy_server -a $api_key

