"""Object storage adapters for generated document artifacts."""

from __future__ import annotations

import hashlib
from functools import lru_cache

import boto3
from botocore.client import Config
from google.cloud import storage as gcs_storage

from app.config import settings


def use_gcs_storage() -> bool:
    return (settings.s3_endpoint_url or "").lower() == "gcs"


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


@lru_cache
def get_gcs_client():
    return gcs_storage.Client()


def _as_bytes(data: bytes | bytearray | memoryview) -> bytes:
    return bytes(data)


def upload_bytes(
    key: str, data: bytes | bytearray | memoryview, content_type: str = "application/octet-stream"
) -> str:
    data_bytes = _as_bytes(data)

    if use_gcs_storage():
        bucket = get_gcs_client().bucket(settings.s3_bucket)
        blob = bucket.blob(key)
        blob.upload_from_string(data_bytes, content_type=content_type)
        return key

    client = get_s3_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data_bytes,
        ContentType=content_type,
    )
    return key


def download_bytes(key: str) -> bytes:
    if use_gcs_storage():
        bucket = get_gcs_client().bucket(settings.s3_bucket)
        return bucket.blob(key).download_as_bytes()

    client = get_s3_client()
    obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read()


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
