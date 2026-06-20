"""Collect tool run data from S3 nginx logs.

Downloads pre-formatted JSON nginx logs from S3 for a given date range,
and for each tool execution request (POST /api/tools/.../build):

- Extracts the tool ID from the request path
- Resolves the requesting site domain from the referer header
- Sends the data point to InfluxDB via the HTTP write API

Usage:
    tool_runs.py [--start YYYY-MM-DD] [--end YYYY-MM-DD]

    Both arguments are optional and inclusive. --start defaults to
    7 days ago and --end defaults to today, so with no arguments the
    script re-lists the last week of S3 objects. State files dedup the
    keys that have already been ingested, so the redundant LIST calls
    are cheap; the look-back exists to pick up Vector batches that flush
    to S3 hours or days after the events they contain.
"""

import argparse
import logging
import os
import re
import ssl
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from s3 import S3Storage  # noqa: E402

load_dotenv(Path(__file__).parent.parent / '.env')

s3 = S3Storage(prefix=os.environ['S3_PREFIX_TOOL_RUNS'])


LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def _log_uncaught(exc_type, exc_value, exc_tb):
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_tb))


sys.excepthook = _log_uncaught

INFLUX_URL = os.environ['INFLUX_URL']
INFLUX_DB = os.environ['INFLUX_DB']
INFLUX_TOKEN = os.environ['INFLUX_TOKEN']
MEASUREMENT_NAME = 'tool_runs'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
STATE_DIR = Path(__file__).parent / 'state'
LOOKBACK_DAYS = 7

TOOL_PATTERN = re.compile(
    r'POST /api/tools/(.+)/build\b'
)
DOMAIN_PATTERN = re.compile(
    r'https?://([^/"\s]+)'
)


def parse_log_record(record: dict) -> dict | None:
    """Extract tool run data from a JSON log record.

    Returns a dict with 'tool_id', 'datetime', and 'domain' keys,
    or None if the record does not match a tool execution request.
    """
    parsed = record.get('parsed', {})
    request = parsed.get('request', '')

    tool_match = TOOL_PATTERN.search(request)
    if not tool_match:
        return None

    timestamp_str = parsed.get('timestamp', '')
    try:
        dt = datetime.strptime(timestamp_str, DATETIME_FORMAT).replace(
            tzinfo=timezone.utc)
    except ValueError:
        logger.warning("Unparseable timestamp in record: %s", timestamp_str)
        return None

    referer = parsed.get('referer', '-')
    domain_match = DOMAIN_PATTERN.search(referer)
    domain = domain_match.group(1) if domain_match else 'unknown'

    tool_id, _, tool_version = tool_match.group(1).rpartition('/')

    return {
        'tool_id': tool_id,
        'tool_version': tool_version,
        'datetime': dt,
        'domain': domain,
    }


def escape_tag_value(value: str) -> str:
    """Escape special characters in an InfluxDB line protocol tag value."""
    return (
        value
        .replace('\\', '\\\\')
        .replace(' ', '\\ ')
        .replace(',', '\\,')
        .replace('=', '\\=')
    )


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
            field_parts.append(f'{k}="{str(v)}"')
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
        description="Collect tool run data from S3 nginx logs.",
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
    ingested = load_ingested_keys(start_date, end_date)

    for key in s3.iter_keys(start_date, end_date):
        if key in ingested:
            logger.debug("Skipping already-ingested key: %s", key)
            continue

        data_points = []
        total_records = 0
        for record in s3.read_records(key):
            total_records += 1
            parsed = parse_log_record(record)
            if not parsed:
                continue

            data_points.append(format_line_protocol(
                measurement=MEASUREMENT_NAME,
                tags={
                    'domain': parsed['domain'],
                    'tool_id': parsed['tool_id'],
                    'tool_version': parsed['tool_version'],
                },
                fields={
                    'count': 1.0,
                },
                timestamp=parsed['datetime'],
            ))

        logger.info(
            "%s: %d/%d records matched tool pattern",
            key.split('/')[-1], len(data_points), total_records,
        )
        if data_points:
            write_to_influxdb(data_points)
            mark_ingested(key)
        else:
            logger.warning(
                "No tool run records found in %s — key not marked ingested",
                key,
            )


if __name__ == '__main__':
    main()
