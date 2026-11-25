"""Tests for analysis job submission and retrieval."""

import uuid
import pytest
from httpx import AsyncClient
from backend.domain.models import MediaAsset
from backend.domain.enums import MediaType


@pytest.mark.asyncio
async def test_submit_analysis_job(client: AsyncClient, auth_headers, test_user, db_session):
    # Setup dummy media asset
    media = MediaAsset(
        uploader_id=test_user.id,
        media_type=MediaType.IMAGE,
        filename="tomato_leaf_01.jpg",
        s3_key="images/test_tomato.jpg",
        content_type="image/jpeg",
        size_bytes=10240,
    )
    db_session.add(media)
    await db_session.commit()
    await db_session.refresh(media)

    # Submit job
    payload = {
        "media_id": str(media.id),
        "analysis_type": "disease_detection",
        "priority": 1,
    }
    resp = await client.post("/api/v1/analysis", json=payload, headers=auth_headers)
    assert resp.status_code == 202
    job = resp.json()
    assert job["media_id"] == str(media.id)
    assert job["status"] in ["pending", "queued"]

    # Poll status
    job_id = job["id"]
    get_resp = await client.get(f"/api/v1/analysis/{job_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == job_id
