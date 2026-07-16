#!/usr/bin/env bash

# Process the backlog of nginx logs using the vector configuration. This is
# intended to be run on the nginx server. Change vars below to match your
# environment before running.

# The script will process one log file at a time, flushing sinks to S3 before
# moving on to the next file.

set -euo pipefail

DRY_RUN=false

if (( $# > 1 )); then
    echo "Usage: $0 [--dry]" >&2
    exit 2
fi

if (( $# == 1 )); then
    if [[ $1 != --dry ]]; then
        echo "Usage: $0 [--dry]" >&2
        exit 2
    fi
    DRY_RUN=true
fi

LOGS_DIR=/mnt/data/nginx_backlog/logs/tools
CONFIG="$PWD/vector-backlog.yml"
DEBUG_DIR="$HOME/vector-debug"
ENV_FILE="$PWD/.env"
MAX_DATE=20260630

mkdir -p "$DEBUG_DIR"

for f in "$LOGS_DIR"/access.log-*.gz; do
    datestamp=$(basename "$f" | grep -oP '\d{8}')
    if (( datestamp <= $MAX_DATE )); then
        echo "Processing: $f"
        if ! $DRY_RUN; then
            zcat "$f" | docker run --rm -i \
                --env-file "$ENV_FILE" \
                -v "$CONFIG:/etc/vector/vector.yml:ro" \
                -v "$DEBUG_DIR:/tmp/vector-backlog" \
                timberio/vector:latest-debian \
                --config /etc/vector/vector.yml
        fi
        echo "Done: $f"
    else
        echo "Skipping: $f"
    fi
done
