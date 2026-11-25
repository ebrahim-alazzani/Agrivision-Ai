"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    user_payload = {
        "email": "new_farmer@agrivision.ai",
        "username": "farmer_saleh",
        "password": "SecurePassword123!",
        "full_name": "Saleh Yemeni",
        "preferred_language": "ar",
    }
    resp = await client.post("/api/v1/auth/register", json=user_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == user_payload["email"]
    assert data["username"] == user_payload["username"]
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "farmer_ali", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "farmer_ali"
