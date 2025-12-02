from __future__ import annotations
import uuid
import os
from typing import BinaryIO
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from .base import StorageDriver


class S3Storage(StorageDriver):
    def __init__(self):
        session_kwargs = {}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs = {
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                "region_name": settings.S3_REGION,
            }
        self.client = boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL, **session_kwargs)
        if not settings.S3_BUCKET:
            raise RuntimeError("S3_BUCKET must be set for S3 storage driver")
        self.bucket = settings.S3_BUCKET

    def _make_key(self, filename: str, purpose: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        uid = uuid.uuid4().hex
        date = "date"  # could be improved to include y/m/d
        return f"{purpose}/{uid}{ext}"

    def put(self, file: BinaryIO, filename: str, purpose: str, owner_id: int | None, public: bool) -> str:
        key = self._make_key(filename, purpose)
        extra = {}
        acl = "public-read" if public else "private"
        try:
            self.client.upload_fileobj(file, self.bucket, key, ExtraArgs={"ACL": acl, **extra})
        except (BotoCoreError, ClientError) as e:
            raise
        return key

    def get(self, path: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=path)
        return obj["Body"].read()

    def delete(self, path: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=path)

    def generate_signed_url(self, path: str, ttl_seconds: int = 3600) -> str:
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": path},
                ExpiresIn=ttl_seconds,
            )
            return url
        except (BotoCoreError, ClientError):
            raise
