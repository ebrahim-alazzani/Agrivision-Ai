"""Tests for farm management endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_farms(client: AsyncClient, auth_headers):
    # 1. Create farm
    farm_data = {
        "name": "Al-Bustan Olive Farm",
        "description": "Family olive and coffee farm in Sana'a highlands",
        "area_hectares": 4.5,
        "location": {
            "latitude": 15.3694,
            "longitude": 44.1910,
            "altitude_m": 2200.0,
            "region": "Sana'a Basin",
            "country": "Yemen",
            "governorate": "Sana'a",
        },
    }
    create_resp = await client.post("/api/v1/farms", json=farm_data, headers=auth_headers)
    assert create_resp.status_code == 201
    created_farm = create_resp.json()
    assert created_farm["name"] == farm_data["name"]
    assert created_farm["area_hectares"] == 4.5
    assert created_farm["location"]["governorate"] == "Sana'a"

    # 2. List farms
    list_resp = await client.get("/api/v1/farms", headers=auth_headers)
    assert list_resp.status_code == 200
    farms = list_resp.json()
    assert len(farms) >= 1
    assert any(f["name"] == "Al-Bustan Olive Farm" for f in farms)
