"""Collect workflow invocation data from S3 nginx logs.

Downloads pre-formatted JSON nginx logs from S3 for a given date range,
and for each workflow invocation request:

- Decodes the StoredWorkflow ID using Galaxy's IdEncodingHelper algorithm
- Queries the Galaxy database for workflow name and source_metadata
- Resolves a canonical workflow identity (TRS tool ID if available)
- Sends the data point to InfluxDB via the HTTP write API

Usage:
    collect_workflow_invocations.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]

    Both arguments are optional and inclusive. --start defaults to
    7 days ago and --end defaults to today, so with no arguments the
    script re-lists the last week of S3 objects. State files dedup the
    keys that have already been ingested, so the redundant LIST calls
    are cheap; the look-back exists to pick up Vector batches that flush
    to S3 hours or days after the events they contain.
"""

import argparse
import codecs
import json
import logging
import os
import re
import sys
import ssl
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from Crypto.Cipher import Blowfish
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).parent.parent))
from s3 import S3Storage  # noqa: E402

load_dotenv(Path(__file__).parent.parent / '.env')

s3 = S3Storage(prefix=os.environ['S3_PREFIX_WORKFLOW_INVOCATIONS'])


LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def _log_uncaught(exc_type, exc_value, exc_tb):
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_tb))


sys.excepthook = _log_uncaught

GALAXY_ID_SECRET = os.environ['GALAXY_ID_SECRET']
GALAXY_DATABASE_URL = os.environ['GALAXY_DATABASE_URL']
INFLUX_URL = os.environ['INFLUX_URL']
INFLUX_DB = os.environ['INFLUX_DB']
INFLUX_TOKEN = os.environ['INFLUX_TOKEN']
MEASUREMENT_NAME = 'workflow_invocation'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
STATE_DIR = Path(__file__).parent / 'state'
LOOKBACK_DAYS = 7

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

    if isinstance(source_metadata, memoryview):
        source_metadata = bytes(source_metadata).decode('utf-8')

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
        if v
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


def load_ingested_keys(start_date: date, end_date: date) -> set[str]:
    """Load the set of S3 keys already ingested for the given date range.

    State files are named YYYY-MM and contain one ingested S3 key per line.
    A range spanning multiple months reads from all relevant state files.
    """
    months = set()
    current = start_date
    while current <= end_date:
        months.add(current.strftime('%Y-%m'))
        current += timedelta(days=1)

    ingested = set()
    for month in months:
        state_file = STATE_DIR / month
        if not state_file.exists():
            continue
        with state_file.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    ingested.add(line)
    return ingested


def mark_ingested(key: str):
    """Append an S3 key to the state file for the month it belongs to."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    month = s3.date_from_key(key).strftime('%Y-%m')
    state_file = STATE_DIR / month
    with state_file.open('a') as f:
        f.write(key + '\n')


def write_to_influxdb(lines: list[str]):
    """Write line protocol data points to InfluxDB via the HTTP write API."""
    payload = '\n'.join(lines).encode('utf-8')
    url = f"{INFLUX_URL}/write?db={INFLUX_DB}&precision=s"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Authorization': f'Token {INFLUX_TOKEN}',
            'Content-Type': 'application/octet-stream',
        },
        method='POST',
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            logger.info(
                "Wrote %d data points to InfluxDB (HTTP %d)",
                len(lines), response.status,
            )
    except urllib.error.URLError as e:
        logger.error("Failed to write to InfluxDB: %s", e)
        sys.exit(1)


def parse_args() -> tuple[date, date]:
    parser = argparse.ArgumentParser(
        description="Collect workflow invocation data from S3 nginx logs.",
    )
    parser.add_argument(
        '--start',
        type=date.fromisoformat,
        default=None,
        help=(
            "Start date (YYYY-MM-DD, inclusive). Defaults to "
            f"{LOOKBACK_DAYS} days ago."
        ),
    )
    parser.add_argument(
        '--end',
        type=date.fromisoformat,
        default=None,
        help="End date (YYYY-MM-DD, inclusive). Defaults to today.",
    )
    args = parser.parse_args()
    today = date.today()
    start_date = args.start or today - timedelta(days=LOOKBACK_DAYS)
    end_date = args.end or today
    if start_date > end_date:
        parser.error(
            f"--start ({start_date}) is after --end ({end_date})")
    return start_date, end_date


def main():
    start_date, end_date = parse_args()

    id_cipher = Blowfish.new(
        GALAXY_ID_SECRET.encode('utf-8'),
        mode=Blowfish.MODE_ECB,
    )
    engine = create_engine(GALAXY_DATABASE_URL)
    ingested = load_ingested_keys(start_date, end_date)

    with engine.connect() as conn:
        for key in s3.iter_keys(start_date, end_date):
            if key in ingested:
                logger.debug("Skipping already-ingested key: %s", key)
                continue

            data_points = []
            for record in s3.read_records(key):
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
            mark_ingested(key)


if __name__ == '__main__':
    main()
