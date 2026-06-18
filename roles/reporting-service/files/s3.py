"""S3 client for reading and managing Galaxy log objects.

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

DATE_PATH_LENGTH = 10  # length of YYYY/MM/DD


class S3Storage:
    def __init__(self):
        self._client = None

    @property
    def endpoint_url(self):
        return os.environ['S3_ENDPOINT_URL']

    @property
    def access_key(self):
        return os.environ['S3_ACCESS_KEY']

    @property
    def secret_key(self):
        return os.environ['S3_SECRET_KEY']

    @property
    def region(self):
        return os.environ['S3_REGION']

    @property
    def bucket(self):
        return os.environ['S3_BUCKET']

    @property
    def prefix(self):
        return os.environ['S3_PREFIX']

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                config=Config(signature_version='s3v4'),
            )
        return self._client

    def list_all_objects(self) -> list[dict]:
        """Return all objects in the bucket."""
        client = self._get_client()
        paginator = client.get_paginator('list_objects_v2')
        objects = []
        for page in paginator.paginate(Bucket=self.bucket):
            objects.extend(page.get('Contents', []))
        return objects

    def delete_objects(self, keys: list[str]):
        """Delete a batch of S3 objects (max 1000 per request)."""
        client = self._get_client()
        for i in range(0, len(keys), 1000):
            batch = [{'Key': k} for k in keys[i:i + 1000]]
            client.delete_objects(
                Bucket=self.bucket,
                Delete={'Objects': batch},
            )

    def date_from_key(self, key: str) -> date:
        """Extract the log date from an S3 object key.

        Keys are of the form <S3_PREFIX>YYYY/MM/DD/HHMMSS-<uuid>.log.gz.
        """
        if not key.startswith(self.prefix):
            raise ValueError(
                f"Key does not start with S3_PREFIX '{self.prefix}': {key}")
        date_str = key[len(self.prefix):len(self.prefix) + DATE_PATH_LENGTH]
        return date.fromisoformat(date_str.replace('/', '-'))

    def iter_keys(self, start_date: date, end_date: date):
        """Yield S3 object keys for log files in the date range (inclusive)."""
        client = self._get_client()
        current = start_date
        while current <= end_date:
            date_prefix = self.prefix + current.strftime('%Y/%m/%d/')
            paginator = client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=date_prefix)
            for page in pages:
                for obj in page.get('Contents', []):
                    yield obj['Key']
            current += timedelta(days=1)

    def read_records(self, key: str):
        """Yield parsed JSON records from a single S3 log object."""
        client = self._get_client()
        logger.info("Downloading s3://%s/%s", self.bucket, key)
        response = client.get_object(Bucket=self.bucket, Key=key)
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
