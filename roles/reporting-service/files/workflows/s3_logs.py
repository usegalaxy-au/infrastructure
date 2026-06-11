"""Download pre-formatted nginx log objects from S3 for a date range.

Objects are stored under a date-partitioned path:
    <S3_PREFIX>YYYY/MM/DD/HHMMSS-<uuid>.log.gz
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

DATE_PATH_LENGTH = 10  # length of YYYY/MM/DD

_client = None


def _s3_client():
    global _client
    if _client is None:
        _client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name=S3_REGION,
            config=Config(signature_version='s3v4'),
        )
    return _client


def date_from_key(key: str) -> date:
    """Extract the log date from an S3 object key.

    Keys are of the form <S3_PREFIX>YYYY/MM/DD/HHMMSS-<uuid>.log.gz.
    """
    if not key.startswith(S3_PREFIX):
        raise ValueError(
            f"Key does not start with S3_PREFIX '{S3_PREFIX}': {key}")
    date_str = key[len(S3_PREFIX):len(S3_PREFIX) + DATE_PATH_LENGTH]
    return date.fromisoformat(date_str.replace('/', '-'))


def iter_keys(start_date: date, end_date: date):
    """Yield S3 object keys for log files in the date range (inclusive)."""
    client = _s3_client()
    current = start_date
    while current <= end_date:
        date_prefix = S3_PREFIX + current.strftime('%Y/%m/%d/')
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=date_prefix)
        for page in pages:
            for obj in page.get('Contents', []):
                yield obj['Key']
        current += timedelta(days=1)


def read_records(key: str):
    """Yield parsed JSON records from a single S3 log object."""
    client = _s3_client()
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
                    "Skipping malformed JSON line in %s: %s", key, e,
                )
