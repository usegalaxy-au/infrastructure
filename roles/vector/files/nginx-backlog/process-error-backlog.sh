#!/usr/bin/env bash

# Process the backlog of nginx error logs using the vector configuration. This
# is intended to be run on the nginx server. Change vars below to match your
# environment before running.

# The script will process one log file at a time, flushing sinks to S3 before
# moving on to the next file.

set -euo pipefail

LOGS_DIR=/var/log/nginx
CONFIG="$PWD/vector-backlog-error-logs.yml"
ENV_FILE="$PWD/.env"

for f in "$LOGS_DIR"/error*.gz; do
    echo "Processing: $f"
    zcat "$f" | docker run --rm -i \
        --env-file "$ENV_FILE" \
        -v "$CONFIG:/etc/vector/vector.yml:ro" \
        timberio/vector:latest-debian \
        --config /etc/vector/vector.yml
    echo "Done: $f"
done
