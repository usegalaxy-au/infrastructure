#!/usr/bin/env bash

# Process the backlog of nginx logs using the vector configuration. This is
# intended to be run on the nginx server. Change vars below to match your
# environment before running.

# The script will process one log file at a time, flushing sinks to S3 before
# moving on to the next file.

set -euo pipefail

LOGS_DIR=/var/log/nginx
CONFIG="$PWD/vector-backlog.yml"
DEBUG_DIR="$HOME/vector-debug"
ENV_FILE="$PWD/.env"

mkdir -p "$DEBUG_DIR"

for f in "$LOGS_DIR"/access*.gz; do
    echo "Processing: $f"
    zcat "$f" | docker run --rm -i \
        --env-file "$ENV_FILE" \
        -v "$CONFIG:/etc/vector/vector.yml:ro" \
        -v "$DEBUG_DIR:/tmp/vector-backlog" \
        timberio/vector:latest-debian \
        --config /etc/vector/vector.yml
    echo "Done: $f"
done
