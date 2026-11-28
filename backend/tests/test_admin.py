"""Authorization and contract checks for the administrative API."""

import uuid

import pytest

from backend.domain.models import Crop, Role
from backend.infrastructure.security import create_access_token


@pytest.mark.asyncio
async def test_admin_dashboard_rejects_user_without_admin_role(client, auth_headers):
    response = await client.get("/api/v1/admin/dashboard", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_dashboard_returns_aggregate_counts(client, db_session, test_user):
    role = Role(id=uuid.uuid4(), name="admin", description="Test administrator")
    test_user.role = role
    db_session.add(role)
    await db_session.commit()
    token = create_access_token(data={"sub": str(test_user.id)})
    response = await client.get(
        "/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["users"] >= 1
    assert set(response.json()) == {
        "users", "farms", "crops", "analyses", "datasets", "models", "training_runs"
    }


@pytest.mark.asyncio
async def test_admin_analytics_returns_database_backed_empty_window(client, db_session, test_user):
    role = Role(id=uuid.uuid4(), name="admin", description="Test administrator")
    test_user.role = role
    db_session.add(role)
    await db_session.commit()
    token = create_access_token(data={"sub": str(test_user.id)})

    response = await client.get(
        "/api/v1/admin/analytics?days=7",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["window_days"] == 7
    assert result["timezone"] == "UTC"
    assert len(result["daily_analyses"]) == 7
    assert all(item["count"] == 0 for item in result["daily_analyses"])
    assert result["statuses"] == []
    assert result["top_result_labels"] == []


@pytest.mark.asyncio
async def test_admin_diagnostics_reports_database_connection(client, db_session, test_user):
    role = Role(id=uuid.uuid4(), name="admin", description="Test administrator")
    test_user.role = role
    db_session.add(role)
    await db_session.commit()
    token = create_access_token(data={"sub": str(test_user.id)})

    response = await client.get(
        "/api/v1/admin/diagnostics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["api"] == "healthy"
    assert response.json()["database"] == "healthy"
    assert response.json()["checked_at"]


@pytest.mark.asyncio
async def test_admin_user_listing_never_returns_password_hash(client, db_session, test_user):
    role = Role(id=uuid.uuid4(), name="admin", description="Test administrator")
    test_user.role = role
    db_session.add(role)
    await db_session.commit()
    token = create_access_token(data={"sub": str(test_user.id)})
    response = await client.get(
        "/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert any(row["id"] == str(test_user.id) for row in response.json())
    assert all("hashed_password" not in row for row in response.json())


@pytest.mark.asyncio
async def test_admin_can_toggle_crop_support(client, db_session, test_user):
    role = Role(id=uuid.uuid4(), name="admin", description="Test administrator")
    crop = Crop(name="test crop", is_supported=False)
    test_user.role = role
    db_session.add_all([role, crop])
    await db_session.commit()
    token = create_access_token(data={"sub": str(test_user.id)})
    response = await client.patch(
        f"/api/v1/admin/crops/{crop.id}/support",
        json={"is_supported": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["is_supported"] is True
