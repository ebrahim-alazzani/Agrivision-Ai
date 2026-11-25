"""
Weather Client.

Fetches, parses, and locally caches real-time and forecast agrometeorological data:
- Temperature, dew point, relative humidity
- Wind speed and gusts
- Precipitation and rain probability
- Local file / memory caching with TTL expiry.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from ai.config import DATA_DIR
from ai.engines.weather_intelligence.config import WeatherConfig

logger = logging.getLogger(__name__)


@dataclass
class WeatherDataPoint:
    timestamp: str
    temperature_c: float
    humidity_pct: float
    dew_point_c: float
    wind_speed_kmh: float
    precipitation_mm: float
    cloud_cover_pct: float


class WeatherClient:
    """
    Client for retrieving agricultural weather observations and forecasts.
    """

    def __init__(
        self,
        config: Optional[WeatherConfig] = None,
        cache_dir: Optional[Path] = None,
    ) -> None:
        self.config = config or WeatherConfig()
        self.cache_dir = cache_dir or (DATA_DIR / "weather_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

    def _cache_key(self, lat: float, lon: float) -> str:
        return f"{lat:.3f}_{lon:.3f}"

    def get_cached(self, key: str) -> Optional[List[WeatherDataPoint]]:
        # Memory cache first
        now = time.time()
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if now - entry["timestamp"] < self.config.cache_ttl_seconds:
                return [WeatherDataPoint(**d) for d in entry["data"]]

        # Disk cache
        file_path = self.cache_dir / f"{key}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                if now - entry.get("timestamp", 0) < self.config.cache_ttl_seconds:
                    return [WeatherDataPoint(**d) for d in entry["data"]]
            except Exception as e:
                logger.warning("Failed to read weather cache %s: %s", file_path, e)

        return None

    def save_cache(self, key: str, data: List[WeatherDataPoint]) -> None:
        entry = {
            "timestamp": time.time(),
            "data": [asdict(d) for d in data],
        }
        self._memory_cache[key] = entry
        file_path = self.cache_dir / f"{key}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2)
        except Exception as e:
            logger.warning("Failed to write weather cache %s: %s", file_path, e)

    def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 3,
    ) -> List[WeatherDataPoint]:
        """
        Fetches hourly agricultural forecast. Uses cached result if recent.
        """
        key = self._cache_key(latitude, longitude)
        cached = self.get_cached(key)
        if cached:
            logger.debug("Returning cached weather for %s", key)
            return cached

        # Open-Meteo public non-commercial agro forecast endpoint
        url = f"{self.config.api_base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m,wind_speed_10m,precipitation,cloud_cover",
            "forecast_days": days,
            "timezone": "auto",
        }

        try:
            with httpx.Client(timeout=self.config.request_timeout) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                payload = resp.json()

            hourly = payload.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            humids = hourly.get("relative_humidity_2m", [])
            dews = hourly.get("dew_point_2m", [])
            winds = hourly.get("wind_speed_10m", [])
            precips = hourly.get("precipitation", [])
            clouds = hourly.get("cloud_cover", [])

            results: List[WeatherDataPoint] = []
            for i in range(len(times)):
                results.append(
                    WeatherDataPoint(
                        timestamp=str(times[i]),
                        temperature_c=float(temps[i]),
                        humidity_pct=float(humids[i]),
                        dew_point_c=float(dews[i]),
                        wind_speed_kmh=float(winds[i]),
                        precipitation_mm=float(precips[i]),
                        cloud_cover_pct=float(clouds[i]),
                    )
                )

            self.save_cache(key, results)
            return results

        except Exception as e:
            logger.warning("Weather API call failed (%s). Generating fallback synthetic data.", e)
            return self._generate_fallback_data()

    def _generate_fallback_data(self) -> List[WeatherDataPoint]:
        """Synthetic seasonal backup when network is unavailable."""
        now_iso = datetime.now(timezone.utc).isoformat()
        return [
            WeatherDataPoint(
                timestamp=now_iso,
                temperature_c=18.5,
                humidity_pct=45.0,
                dew_point_c=6.5,
                wind_speed_kmh=12.0,
                precipitation_mm=0.0,
                cloud_cover_pct=20.0,
            )
        ]
