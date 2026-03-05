"""End-to-end test for the workflow invocation reporting pipeline.

Imports and exercises collect_workflow_invocations.py against the live
Galaxy database, printing the InfluxDB data point that would be written
for a given encoded workflow ID. No data is written to InfluxDB.

Requires:
    - collect_workflow_invocations.py in the same directory (deployed)
    - .env file with GALAXY_ID_SECRET, GALAXY_DATABASE_URL,
      INFLUXDB_SECRETS_FILE, and INFLUXDB_DATABASE

Usage:
    cd /home/ubuntu/workflow_invocations
    ./venv/bin/python test_workflow_id_mapping.py
"""

import json
import sys
from datetime import datetime

# Import functions from the deployed script
from collect_workflow_invocations import (
    GALAXY_DATABASE_URL,
    GALAXY_ID_SECRET,
    MEASUREMENT_NAME,
    WORKFLOW_QUERY,
    decode_galaxy_id,
    resolve_canonical_id,
)
from Crypto.Cipher import Blowfish
from sqlalchemy import create_engine

# =====================================================================
# Set this to a real encoded workflow ID from nginx logs, e.g.
#   grep 'workflows/.*/invocations' /var/log/nginx/access.log \
#       | tail -1
# and copy the hex string from the URL.

TEST_ENCODED_WORKFLOW_ID = '1346aa3b2ee8c0a3'

# =====================================================================

SAMPLE_DOMAIN = 'genome.usegalaxy.org.au'


def main():
    print("=" * 60)
    print("Workflow invocation reporting - end-to-end test")
    print("=" * 60)

    # Step 1: Decode the encoded workflow ID
    print(f"\n[1] Decoding encoded ID: {TEST_ENCODED_WORKFLOW_ID}")
    id_cipher = Blowfish.new(
        GALAXY_ID_SECRET.encode('utf-8'),
        mode=Blowfish.MODE_ECB,
    )
    try:
        workflow_id = decode_galaxy_id(
            TEST_ENCODED_WORKFLOW_ID, id_cipher)
    except (ValueError, TypeError) as e:
        print(f"  FAIL: Could not decode ID: {e}")
        sys.exit(1)
    print(f"  Decoded database ID: {workflow_id}")

    # Step 2: Query the Galaxy database
    print(f"\n[2] Querying Galaxy database for StoredWorkflow {workflow_id}")
    engine = create_engine(GALAXY_DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(
            WORKFLOW_QUERY,
            {'id': workflow_id},
        ).fetchone()

    if not result:
        print(f"  FAIL: StoredWorkflow {workflow_id} not found in database")
        sys.exit(1)

    _, name, user_id, uuid, source_metadata = result
    print(f"  Workflow name:  {name}")
    print(f"  User ID:        {user_id}")
    print(f"  UUID:           {uuid}")
    print(f"  source_metadata: {json.dumps(source_metadata, indent=4)}")

    # Step 3: Resolve canonical identity
    print("\n[3] Resolving canonical identity")
    canonical_id, trs_server, trs_version_id = (
        resolve_canonical_id(source_metadata)
    )
    print(f"  canonical_id:   {canonical_id or '(none - local workflow)'}")
    print(f"  trs_server:     {trs_server or '(none)'}")
    print(f"  trs_version_id: {trs_version_id or '(none)'}")

    # Step 4: Build the InfluxDB data point (what would be written)
    now = datetime.utcnow()
    point = {
        'measurement': MEASUREMENT_NAME,
        'time': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tags': {
            'domain': SAMPLE_DOMAIN,
            'workflow_name': name,
            'canonical_id': canonical_id or name,
            'trs_server': trs_server,
        },
        'fields': {
            'count': 1.0,
            'workflow_id': workflow_id,
            'user_id': user_id,
            'trs_version_id': trs_version_id,
        },
    }

    print("\n[4] InfluxDB data point (would be written):")
    print(json.dumps(point, indent=4))

    print("\n" + "=" * 60)
    print("PASS: All steps completed successfully")
    print("=" * 60)


if __name__ == '__main__':
    main()
