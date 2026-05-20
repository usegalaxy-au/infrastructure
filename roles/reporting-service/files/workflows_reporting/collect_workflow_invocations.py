"""Collect workflow invocation data from S3 nginx logs.

Downloads pre-formatted JSON nginx logs from S3 for a given date range,
and for each workflow invocation request:

- Decodes the StoredWorkflow ID using Galaxy's IdEncodingHelper algorithm
- Queries the Galaxy database for workflow name and source_metadata
- Resolves a canonical workflow identity (TRS tool ID if available)
- Sends the data point to InfluxDB via the HTTP write API

Usage:
    collect_workflow_invocations.py <start_date> <end_date>

    Dates are in YYYY-MM-DD format (both inclusive).
"""

import codecs
import json
import logging
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from Crypto.Cipher import Blowfish
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from s3_logs import date_range_from_args, iter_log_records

load_dotenv(Path(__file__).parent / '.env')

LOG_FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

GALAXY_ID_SECRET = os.environ['GALAXY_ID_SECRET']
GALAXY_DATABASE_URL = os.environ['GALAXY_DATABASE_URL']
INFLUX_URL = os.environ['INFLUX_URL']
INFLUX_DB = os.environ['INFLUX_DB']
INFLUX_TOKEN = os.environ['INFLUX_TOKEN']
MEASUREMENT_NAME = 'workflow_invocation'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

INVOCATION_PATTERN = re.compile(
    r'POST /api/workflows/([a-f0-9]+)/invocations'
)
DOMAIN_PATTERN = re.compile(
    r'https?://([^/"\s]+)'
)

WORKFLOW_QUERY = text("""
    SELECT sw.id, sw.name, sw.user_id, w.uuid, w.source_metadata
    FROM stored_workflow sw
    JOIN workflow w ON w.id = sw.latest_workflow_id
    WHERE sw.id = :id
""")


def decode_galaxy_id(encoded_id: str, id_cipher) -> int:
    """Decode a Galaxy hex-encoded ID to an integer database ID.

    Replicates Galaxy's IdEncodingHelper.decode_id algorithm:
    hex decode -> Blowfish ECB decrypt -> strip padding -> int.
    """
    raw = codecs.decode(encoded_id, 'hex')
    decrypted = id_cipher.decrypt(raw)
    return int(decrypted.decode('utf-8').lstrip('!'))


def parse_log_record(record: dict) -> dict | None:
    """Extract workflow invocation data from a JSON log record.

    Returns a dict with 'encoded_id', 'datetime', and 'domain' keys,
    or None if the record does not match a workflow invocation request.
    """
    parsed = record.get('parsed', {})
    request = parsed.get('request', '')

    inv_match = INVOCATION_PATTERN.search(request)
    if not inv_match:
        return None

    ts_str = parsed.get('timestamp', '')
    try:
        dt = datetime.strptime(ts_str, DATETIME_FORMAT).replace(
            tzinfo=timezone.utc)
    except ValueError:
        logger.warning("Unparseable timestamp in record: %s", ts_str)
        return None

    referer = parsed.get('referer', '-')
    domain_match = DOMAIN_PATTERN.search(referer)
    domain = domain_match.group(1) if domain_match else 'unknown'

    return {
        'encoded_id': inv_match.group(1),
        'datetime': dt,
        'domain': domain,
    }


def resolve_canonical_id(source_metadata) -> tuple[str, str, str]:
    """Resolve canonical workflow identity from source_metadata.

    Returns (canonical_id, trs_server, trs_version_id).
    """
    if not source_metadata:
        return ('', '', '')

    if isinstance(source_metadata, str):
        source_metadata = json.loads(source_metadata)

    trs_tool_id = source_metadata.get('trs_tool_id', '')
    trs_server = source_metadata.get('trs_server', '')
    trs_version_id = source_metadata.get('trs_version_id', '')

    if trs_tool_id:
        canonical_id = (
            f"{trs_server}:{trs_tool_id}" if trs_server
            else trs_tool_id
        )
        return (canonical_id, trs_server, trs_version_id)

    url = source_metadata.get('url', '')
    if url:
        return (url, '', '')

    return ('', '', '')


def escape_tag_value(value: str) -> str:
    """Escape special characters in an InfluxDB line protocol tag value."""
    return (
        value
        .replace('\\', '\\\\')
        .replace(' ', '\\ ')
        .replace(',', '\\,')
        .replace('=', '\\=')
    )


def escape_field_string(value: str) -> str:
    """Escape special characters in an InfluxDB line protocol string field."""
    return value.replace('\\', '\\\\').replace('"', '\\"')


def format_line_protocol(
    measurement: str,
    tags: dict,
    fields: dict,
    timestamp: datetime,
) -> str:
    """Format a data point as an InfluxDB line protocol string."""
    tag_str = ','.join(
        f"{k}={escape_tag_value(str(v))}"
        for k, v in tags.items()
    )
    field_parts = []
    for k, v in fields.items():
        if isinstance(v, float):
            field_parts.append(f"{k}={v}")
        elif isinstance(v, int):
            field_parts.append(f"{k}={v}i")
        else:
            field_parts.append(f'{k}="{escape_field_string(str(v))}"')
    field_str = ','.join(field_parts)
    ts = int(timestamp.timestamp())
    return f"{measurement},{tag_str} {field_str} {ts}"


def write_to_influxdb(lines: list[str]):
    """Write line protocol data points to InfluxDB via the HTTP write API."""
    payload = '\n'.join(lines).encode('utf-8')
    url = f"{INFLUX_URL}/write?db={INFLUX_DB}"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Authorization': f'Token {INFLUX_TOKEN}',
            'Content-Type': 'application/octet-stream',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req) as response:
            logger.info(
                "Wrote %d data points to InfluxDB (HTTP %d)",
                len(lines), response.status,
            )
    except urllib.error.URLError as e:
        logger.error("Failed to write to InfluxDB: %s", e)
        sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} <start_date> <end_date>",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        start_date, end_date = date_range_from_args(sys.argv[1], sys.argv[2])
    except ValueError as e:
        logger.error("Invalid date argument: %s", e)
        sys.exit(1)

    id_cipher = Blowfish.new(
        GALAXY_ID_SECRET.encode('utf-8'),
        mode=Blowfish.MODE_ECB,
    )
    engine = create_engine(GALAXY_DATABASE_URL)
    data_points = []

    with engine.connect() as conn:
        for record in iter_log_records(start_date, end_date):
            parsed = parse_log_record(record)
            if not parsed:
                continue

            try:
                workflow_id = decode_galaxy_id(
                    parsed['encoded_id'], id_cipher)
            except (ValueError, TypeError) as e:
                logger.warning(
                    "Failed to decode ID '%s': %s",
                    parsed['encoded_id'], e,
                )
                continue

            result = conn.execute(
                WORKFLOW_QUERY,
                {'id': workflow_id},
            ).fetchone()

            if not result:
                logger.warning(
                    "StoredWorkflow %d not found in database",
                    workflow_id,
                )
                continue

            _, name, user_id, uuid, source_metadata = result
            canonical_id, trs_server, trs_version_id = (
                resolve_canonical_id(source_metadata)
            )

            data_points.append(format_line_protocol(
                measurement=MEASUREMENT_NAME,
                tags={
                    'domain': parsed['domain'],
                    'workflow_name': name,
                    'canonical_id': canonical_id or name,
                    'trs_server': trs_server,
                },
                fields={
                    'count': 1.0,
                    'workflow_id': workflow_id,
                    'user_id': user_id,
                    'trs_version_id': trs_version_id,
                },
                timestamp=parsed['datetime'],
            ))

    if data_points:
        write_to_influxdb(data_points)


if __name__ == '__main__':
    main()
