"""
Script: create_bucket.py

Description:
This script creates a new S3 bucket in an S3-compatible storage system using AWS access credentials, 
a specified bucket name, and endpoint URL.

Arguments:
  --access_key: AWS Access Key for authentication
  --secret_key: AWS Secret Key for authentication
  --bucket_name: The name of the bucket to be created
  --endpoint_url: The endpoint URL of the S3-compatible storage service

Example:
  python create_bucket.py --access_key AKIAEXAMPLE --secret_key SECRETKEYEXAMPLE --bucket_name my-new-bucket --endpoint_url https://s3.example.com
"""

import argparse
import boto3
from botocore.exceptions import ClientError

def create_bucket(access_key, secret_key, bucket_name, endpoint_url):
    # Initialize the S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url
    )

    try:
        # Attempt to create the bucket
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        print(f"Error creating bucket: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Create an S3 bucket with specified credentials and endpoint.")
    parser.add_argument('--access_key', required=True, type=str, help="AWS Access Key")
    parser.add_argument('--secret_key', required=True, type=str, help="AWS Secret Key")
    parser.add_argument('--bucket_name', required=True, type=str, help="Name of the S3 bucket to be created")
    parser.add_argument('--endpoint_url', required=True, type=str, help="S3 Endpoint URL")
    args = parser.parse_args()

    # Create the bucket
    create_bucket(args.access_key, args.secret_key, args.bucket_name, args.endpoint_url)

if __name__ == "__main__":
    main()

