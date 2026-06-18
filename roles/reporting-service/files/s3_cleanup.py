"""Enforce S3 log data retention policy.

Deletes objects from S3 whose age exceeds the configured retention period.
Object categories are identified by path segment
('cleaned', 'raw', 'selected').
Objects whose category has a null retention value are kept forever.

Retention policy is read from a JSON file e.g.:
    {"cleaned": 1825, "raw": 30, "selected": null}

Designed to run daily by cron.

Usage:
    s3_cleanup.py [--policy-file PATH]
"""

import argparse
import json
import logging
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from s3 import S3Storage

load_dotenv(Path(__file__).parent / '.env')

LOG_FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

CATEGORIES = ('cleaned', 'raw', 'selected')

# Object keys are date-partitioned:
#   .../<category>/YYYY/MM/DD/HHMMSS-<uuid>.log.gz
DATE_PATTERN = re.compile(r'/(\d{4})/(\d{2})/(\d{2})/[^/]+$')


def object_category(key: str) -> str | None:
    """Return the category from an S3 key, or None if not recognised."""
    for category in CATEGORIES:
        if f'/{category}/' in key:
            return category
    return None


def object_date(key: str) -> date | None:
    """Extract the date from the path partition of an S3 key."""
    match = DATE_PATTERN.search(key)
    if not match:
        return None
    try:
        return date(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--policy',
        type=Path,
        help='Path to JSON retention policy file.',
        required=True,
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List objects that would be deleted without deleting them',
    )
    args = parser.parse_args()

    try:
        policy = json.loads(args.policy.read_text())
    except FileNotFoundError:
        logger.error("Policy file not found: %s", args.policy)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in policy file %s: %s", args.policy, e)
        sys.exit(1)

    today = date.today()
    s3 = S3Storage()
    objects = s3.list_all_objects()
    to_delete = []

    for obj in objects:
        key = obj['Key']
        category = object_category(key)
        if category is None:
            continue

        retention_days = policy.get(category)
        if retention_days is None:
            continue

        obj_date = object_date(key)
        if obj_date is None:
            logger.warning("Could not parse date from key: %s", key)
            continue

        cutoff = today - timedelta(days=retention_days)
        if obj_date < cutoff:
            to_delete.append(key)

    if not to_delete:
        logger.info("No objects to delete.")
        return

    if args.dry_run:
        logger.info("Dry run — would delete %d object(s):", len(to_delete))
        for key in to_delete:
            logger.info("  %s", key)
        return

    logger.info("Deleting %d object(s)...", len(to_delete))
    s3.delete_objects(to_delete)
    logger.info("Done.")


if __name__ == '__main__':
    main()
