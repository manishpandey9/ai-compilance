"""S3-compatible object storage (R2 / MinIO)."""

from __future__ import annotations

import hashlib
from functools import lru_cache

import boto3
from botocore.client import Config

from app.config import settings


@lru_cache
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key


def download_bytes(key: str) -> bytes:
    client = get_s3_client()
    obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read()


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
