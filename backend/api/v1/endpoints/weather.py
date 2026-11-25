"""Weather observation, forecast, and proactive alert endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.application.weather_service import WeatherService
from backend.domain.models import User
from backend.domain.schemas import (
    WeatherAlert,
    WeatherForecastResponse,
    WeatherObservationResponse,
)
from backend.infrastructure.database import get_db_session

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current/{farm_id}", response_model=WeatherObservationResponse)
async def get_current_weather(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current weather metrics for farm location."""
    service = WeatherService(db)
    return await service.get_current_weather(farm_id)


@router.get("/forecast/{farm_id}", response_model=List[WeatherForecastResponse])
async def get_weather_forecast(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get 5-day weather forecast for farm location."""
    service = WeatherService(db)
    return await service.get_forecast(farm_id)


@router.get("/alerts/{farm_id}", response_model=List[WeatherAlert])
async def get_weather_alerts(
    farm_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get active agricultural weather alerts (frost risk, heat stress, fungal disease favorability)."""
    service = WeatherService(db)
    return await service.get_active_alerts(farm_id)
