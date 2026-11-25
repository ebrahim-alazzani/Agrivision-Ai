"""S3-compatible object storage client (works with MinIO and AWS S3)."""

import io
import uuid
from typing import BinaryIO, Optional

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from backend.infrastructure.config import get_settings

settings = get_settings()


class S3Storage:
    """Handle file uploads and downloads to S3-compatible storage."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=BotoConfig(signature_version="s3v4"),
        )
        self._bucket = settings.s3_bucket_name

    def ensure_bucket(self) -> None:
        """Create the bucket if it does not exist."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def upload_file(
        self,
        file_data: BinaryIO,
        key: Optional[str] = None,
        content_type: str = "application/octet-stream",
        folder: str = "uploads",
    ) -> str:
        """Upload a file and return the object key.

        Args:
            file_data: File-like object to upload.
            key: Object key. Auto-generated if not provided.
            content_type: MIME type of the file.
            folder: Folder prefix in the bucket.

        Returns:
            The S3 object key.
        """
        if key is None:
            ext = content_type.split("/")[-1] if "/" in content_type else "bin"
            key = f"{folder}/{uuid.uuid4().hex}.{ext}"

        self._client.upload_fileobj(
            file_data,
            self._bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return key

    def download_file(self, key: str) -> bytes:
        """Download a file by its object key."""
        buf = io.BytesIO()
        self._client.download_fileobj(self._bucket, key, buf)
        buf.seek(0)
        return buf.read()

    def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
    ) -> str:
        """Generate a presigned URL for downloading a file.

        Args:
            key: S3 object key.
            expiration: URL expiry in seconds (default 1 hour).

        Returns:
            Presigned download URL.
        """
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expiration,
        )

    def delete_file(self, key: str) -> None:
        """Delete a file by its object key."""
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def file_exists(self, key: str) -> bool:
        """Check whether an object exists in the bucket."""
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False
