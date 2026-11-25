"""Media upload and retrieval endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.application.media_service import MediaService
from backend.domain.models import MediaAsset, User
from backend.domain.schemas import MediaUploadResponse
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    farm_id: Optional[uuid.UUID] = Form(None),
    crop_id: Optional[uuid.UUID] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Upload an image or video with validation and S3 storage."""
    service = MediaService(db)
    asset = await service.validate_and_upload(
        file=file,
        uploader_id=current_user.id,
        farm_id=farm_id,
        crop_id=crop_id,
        latitude=latitude,
        longitude=longitude,
    )
    url = service.get_download_url(asset)
    return MediaUploadResponse(
        id=asset.id,
        filename=asset.filename,
        media_type=asset.media_type,
        content_type=asset.content_type,
        size_bytes=asset.size_bytes,
        download_url=url,
        farm_id=asset.farm_id,
        crop_id=asset.crop_id,
        created_at=asset.created_at,
    )


@router.get("/{media_id}", response_model=MediaUploadResponse)
async def get_media(
    media_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get media asset details and download URL."""
    service = MediaService(db)
    asset = await db.get(MediaAsset, media_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Media asset not found")

    url = service.get_download_url(asset)
    return MediaUploadResponse(
        id=asset.id,
        filename=asset.filename,
        media_type=asset.media_type,
        content_type=asset.content_type,
        size_bytes=asset.size_bytes,
        download_url=url,
        farm_id=asset.farm_id,
        crop_id=asset.crop_id,
        created_at=asset.created_at,
    )
