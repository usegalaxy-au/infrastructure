"""Enforce S3 log data retention policy.

Deletes objects from S3 whose age exceeds the configured retention period.
Object categories are identified by path segment
('cleaned', 'raw', 'selected').
Objects whose category has a null retention value are kept forever.

Retention policy (days) is passed as JSON via --policy, e.g.:
    {"cleaned": 1825, "raw": 30, "selected": null}

Designed to run daily by cron.

Usage:
    s3_cleanup.py --policy '<json>'
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import date, timedelta

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

LOG_FORMAT = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

S3_ENDPOINT_URL = os.environ['S3_ENDPOINT_URL']
S3_ACCESS_KEY = os.environ['S3_ACCESS_KEY']
S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
S3_REGION = os.environ['S3_REGION']
S3_BUCKET = os.environ['S3_BUCKET']

CATEGORIES = ('cleaned', 'raw', 'selected')

# Object keys contain a date prefix: .../<category>/YYYY-MM-DD<uuid>.log.gz
DATE_PATTERN = re.compile(r'/(\d{4}-\d{2}-\d{2})[^/]*$')


def s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
        config=Config(signature_version='s3v4'),
    )


def object_category(key: str) -> str | None:
    """Return the category from an S3 key, or None if not recognised."""
    for category in CATEGORIES:
        if f'/{category}/' in key:
            return category
    return None


def object_date(key: str) -> date | None:
    """Extract the date from the filename portion of an S3 key."""
    match = DATE_PATTERN.search(key)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def list_all_objects(client) -> list[dict]:
    paginator = client.get_paginator('list_objects_v2')
    objects = []
    for page in paginator.paginate(Bucket=S3_BUCKET):
        objects.extend(page.get('Contents', []))
    return objects


def delete_objects(client, keys: list[str]):
    """Delete a batch of objects from S3 (max 1000 per request)."""
    for i in range(0, len(keys), 1000):
        batch = [{'Key': k} for k in keys[i:i + 1000]]
        client.delete_objects(
            Bucket=S3_BUCKET,
            Delete={'Objects': batch},
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--policy',
        required=True,
        help='JSON retention policy: {"category": days_or_null, ...}',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List objects that would be deleted without deleting them',
    )
    args = parser.parse_args()

    try:
        policy = json.loads(args.policy)
    except json.JSONDecodeError as e:
        logger.error("Invalid --policy JSON: %s", e)
        sys.exit(1)

    today = date.today()
    client = s3_client()
    objects = list_all_objects(client)
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
    delete_objects(client, to_delete)
    logger.info("Done.")


if __name__ == '__main__':
    main()
