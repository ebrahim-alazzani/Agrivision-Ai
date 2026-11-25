"""Media service for handling file uploads, validation, and storage."""

import io
import uuid
from typing import Optional, Tuple
from PIL import Image
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.enums import MediaType
from backend.domain.models import MediaAsset
from backend.infrastructure.config import get_settings
from backend.infrastructure.storage import S3Storage

settings = get_settings()


class MediaService:
    """Service to handle media asset upload, validation, and metadata extraction."""

    def __init__(self, db: AsyncSession, storage: Optional[S3Storage] = None):
        self.db = db
        self.storage = storage or S3Storage()

    async def validate_and_upload(
        self,
        file: UploadFile,
        uploader_id: uuid.UUID,
        farm_id: Optional[uuid.UUID] = None,
        crop_id: Optional[uuid.UUID] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> MediaAsset:
        """Validate an uploaded image/video, upload to storage, and save database record."""
        content_type = file.content_type or ""
        
        # Check size and content type
        contents = await file.read()
        file_size = len(contents)

        if file_size > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.max_upload_size_mb}MB",
            )

        width: Optional[int] = None
        height: Optional[int] = None
        duration_seconds: Optional[float] = None
        metadata_json = {}

        if content_type in settings.allowed_image_types_list:
            media_type = MediaType.IMAGE
            # Validate image and extract dimensions
            try:
                img = Image.open(io.BytesIO(contents))
                img.verify()
                # Reopen to read dimensions after verify
                img = Image.open(io.BytesIO(contents))
                width, height = img.size
                metadata_json = {
                    "format": img.format,
                    "mode": img.mode,
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid or corrupted image file: {str(e)}",
                )
        elif content_type in settings.allowed_video_types_list:
            media_type = MediaType.VIDEO
            # Basic video metadata
            metadata_json = {"mime_type": content_type}
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported media type: {content_type}. Allowed: {settings.allowed_image_types}, {settings.allowed_video_types}",
            )

        # Upload to storage
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
        s3_key = f"{media_type.value}s/{uuid.uuid4().hex}.{ext}"

        file_obj = io.BytesIO(contents)
        self.storage.upload_file(
            file_data=file_obj,
            key=s3_key,
            content_type=content_type,
            folder=f"{media_type.value}s",
        )

        # Create DB record
        asset = MediaAsset(
            uploader_id=uploader_id,
            media_type=media_type,
            filename=file.filename or "unknown",
            s3_key=s3_key,
            content_type=content_type,
            size_bytes=file_size,
            width=width,
            height=height,
            duration_seconds=duration_seconds,
            metadata_json=metadata_json,
            farm_id=farm_id,
            crop_id=crop_id,
            latitude=latitude,
            longitude=longitude,
        )
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)

        return asset

    def get_download_url(self, asset: MediaAsset, expiration: int = 3600) -> str:
        """Generate presigned download URL for a media asset."""
        return self.storage.generate_presigned_url(asset.s3_key, expiration=expiration)
