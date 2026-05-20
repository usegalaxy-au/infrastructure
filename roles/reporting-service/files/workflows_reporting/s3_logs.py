"""Download pre-formatted nginx log objects from S3 for a date range.

Objects are named with a date prefix: YYYY-MM-DD<uuid>.log.gz
Each object is a gzipped newline-delimited JSON file.
"""

import gzip
import io
import json
import logging
import os
from datetime import date, timedelta

import boto3
from botocore.client import Config

logger = logging.getLogger(__name__)

S3_ENDPOINT_URL = os.environ['S3_ENDPOINT_URL']
S3_ACCESS_KEY = os.environ['S3_ACCESS_KEY']
S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
S3_REGION = os.environ['S3_REGION']
S3_BUCKET = os.environ['S3_BUCKET']
S3_PREFIX = os.environ['S3_PREFIX']


def _s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
        config=Config(signature_version='s3v4'),
    )


def iter_log_records(start_date: date, end_date: date):
    """Yield parsed log record dicts for all objects in the date range.

    Both start_date and end_date are inclusive. Each yielded dict is the
    parsed JSON object from a single log line, i.e.:
        {
            "parsed": {"request": ..., "timestamp": ..., "referer": ..., ...},
            ...
        }
    """
    client = _s3_client()
    current = start_date
    while current <= end_date:
        date_prefix = S3_PREFIX + current.strftime('%Y-%m-%d')
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=date_prefix)
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                logger.info("Downloading s3://%s/%s", S3_BUCKET, key)
                response = client.get_object(Bucket=S3_BUCKET, Key=key)
                body = response['Body'].read()
                with gzip.open(io.BytesIO(body)) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError as e:
                            logger.warning(
                                "Skipping malformed JSON line in %s: %s",
                                key, e,
                            )
        current += timedelta(days=1)


def date_range_from_args(start_str: str, end_str: str) -> tuple[date, date]:
    """Parse YYYY-MM-DD date strings into a (start, end) date tuple."""
    return (
        date.fromisoformat(start_str),
        date.fromisoformat(end_str),
    )
