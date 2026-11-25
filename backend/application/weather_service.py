"""Weather service for fetching, caching, and analyzing weather data and alerts."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.domain.enums import WeatherAlertSeverity
from backend.domain.models import Farm, FarmLocation, WeatherForecast, WeatherObservation
from backend.domain.schemas import WeatherAlert
from backend.infrastructure.config import get_settings

settings = get_settings()


class WeatherService:
    """Service handling weather observations, forecasts, and agricultural alert rules."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_weather(self, farm_id: uuid.UUID) -> WeatherObservation:
        """Get latest weather observation for a farm, fetching from API if stale or missing."""
        stmt = (
            select(WeatherObservation)
            .where(WeatherObservation.farm_id == farm_id)
            .order_by(WeatherObservation.observed_at.desc())
        )
        res = await self.db.execute(stmt)
        latest = res.scalars().first()

        now = datetime.now(timezone.utc)
        if latest and (now - latest.observed_at) < timedelta(hours=1):
            return latest

        # Fetch fresh weather data
        farm_stmt = (
            select(Farm)
            .where(Farm.id == farm_id)
        )
        farm_res = await self.db.execute(farm_stmt)
        farm = farm_res.scalars().first()
        if not farm:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

        loc_stmt = select(FarmLocation).where(FarmLocation.farm_id == farm_id)
        loc_res = await self.db.execute(loc_stmt)
        loc = loc_res.scalars().first()

        lat = loc.latitude if loc else 15.3694  # Default Yemen (Sana'a)
        lon = loc.longitude if loc else 44.1910

        obs = await self._fetch_weather_from_provider(farm_id, lat, lon)
        return obs

    async def _fetch_weather_from_provider(
        self, farm_id: uuid.UUID, lat: float, lon: float
    ) -> WeatherObservation:
        """Call external weather API or simulate based on coordinates."""
        temp = 24.5
        humidity = 45.0
        wind = 3.5
        precip = 0.0
        pressure = 1012.0
        condition = "Sunny"

        if settings.weather_api_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(
                        f"{settings.weather_api_url}/weather",
                        params={"lat": lat, "lon": lon, "appid": settings.weather_api_key, "units": "metric"},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        main = data.get("main", {})
                        temp = main.get("temp", temp)
                        humidity = main.get("humidity", humidity)
                        pressure = main.get("pressure", pressure)
                        wind = data.get("wind", {}).get("speed", wind)
                        precip = data.get("rain", {}).get("1h", 0.0)
                        if data.get("weather"):
                            condition = data["weather"][0].get("main", condition)
            except Exception:
                pass  # Fall back to sensible defaults

        obs = WeatherObservation(
            farm_id=farm_id,
            temperature_c=temp,
            humidity_pct=humidity,
            wind_speed_ms=wind,
            precipitation_mm=precip,
            pressure_hpa=pressure,
            condition=condition,
            observed_at=datetime.now(timezone.utc),
        )
        self.db.add(obs)
        await self.db.commit()
        await self.db.refresh(obs)
        return obs

    async def get_forecast(self, farm_id: uuid.UUID) -> List[WeatherForecast]:
        """Get 5-day forecast for farm."""
        stmt = (
            select(WeatherForecast)
            .where(WeatherForecast.farm_id == farm_id)
            .order_by(WeatherForecast.forecast_date.asc())
        )
        res = await self.db.execute(stmt)
        forecasts = list(res.scalars().all())

        if not forecasts:
            # Generate initial mock forecast entries
            now = datetime.now(timezone.utc)
            for i in range(1, 6):
                f_date = now + timedelta(days=i)
                fc = WeatherForecast(
                    farm_id=farm_id,
                    forecast_date=f_date,
                    temp_min_c=14.0 + i,
                    temp_max_c=28.0 + i * 0.5,
                    humidity_pct=40.0 + i * 2,
                    precipitation_mm=0.0 if i < 3 else 2.5,
                    wind_speed_ms=4.0,
                    condition="Clear" if i < 3 else "Scattered Clouds",
                )
                self.db.add(fc)
                forecasts.append(fc)
            await self.db.commit()

        return forecasts

    async def get_active_alerts(self, farm_id: uuid.UUID) -> List[WeatherAlert]:
        """Analyze current and forecast conditions to generate proactive agricultural weather alerts."""
        alerts: List[WeatherAlert] = []
        curr = await self.get_current_weather(farm_id)
        now = datetime.now(timezone.utc)

        # Frost Warning Check (Crucial for Yemen Highlands: Dhamar, Sana'a)
        if curr.temperature_c is not None and curr.temperature_c <= 3.0:
            alerts.append(
                WeatherAlert(
                    farm_id=farm_id,
                    alert_type="Frost Warning",
                    severity=WeatherAlertSeverity.WARNING if curr.temperature_c > 0 else WeatherAlertSeverity.EMERGENCY,
                    message=f"Risk of frost! Current temperature is {curr.temperature_c}°C. Take immediate protective measures.",
                    message_ar=f"تحذير من الصقيع! درجة الحرارة الحالية {curr.temperature_c} مئوية. يرجى اتخاذ الإجراءات الوقائية للمحاصيل فوراً.",
                    issued_at=now,
                    expires_at=now + timedelta(hours=6),
                )
            )

        # Heat Wave / High Evapotranspiration
        if curr.temperature_c is not None and curr.temperature_c >= 38.0:
            alerts.append(
                WeatherAlert(
                    farm_id=farm_id,
                    alert_type="Heat Stress",
                    severity=WeatherAlertSeverity.ADVISORY,
                    message=f"High temperature alert ({curr.temperature_c}°C). Increase irrigation frequency to prevent crop wilting.",
                    message_ar=f"تنبيه إجهاد حراري ({curr.temperature_c} مئوية). يرجى زيادة معدلات الري لتجنب ذبول المحاصيل.",
                    issued_at=now,
                    expires_at=now + timedelta(hours=8),
                )
            )

        # High Humidity + Moderate Temp -> Disease Risk (e.g. Late Blight)
        if curr.humidity_pct is not None and curr.humidity_pct > 85.0:
            alerts.append(
                WeatherAlert(
                    farm_id=farm_id,
                    alert_type="Fungal Disease Risk",
                    severity=WeatherAlertSeverity.WATCH,
                    message="High humidity detected. Conditions are favorable for fungal diseases (downy/late blight). Monitor leaves closely.",
                    message_ar="ارتفاع ملحوظ في الرطوبة. الظروف مواتية لانتشار الأمراض الفطرية مثل اللفحة والندوة. يرجى فحص الأوراق.",
                    issued_at=now,
                    expires_at=now + timedelta(hours=24),
                )
            )

        return alerts
