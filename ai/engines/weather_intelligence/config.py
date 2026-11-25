"""
Configuration and Thresholds for Weather Intelligence Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class FrostRiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WeatherConfig:
    """Config for weather endpoints and agricultural risk rules."""
    api_base_url: str = "https://api.open-meteo.com/v1"
    cache_ttl_seconds: int = 3600  # 1 hour
    request_timeout: float = 10.0

    # Frost triggers (degrees Celsius)
    frost_critical_temp_c: float = 0.0
    frost_high_temp_c: float = 2.0
    frost_moderate_temp_c: float = 4.0
    frost_low_temp_c: float = 6.0

    # Heat stress triggers
    heat_stress_temp_c: float = 38.0

    # High humidity disease risk (fungal pathogens thrive above 85% RH)
    fungal_risk_humidity_pct: float = 85.0
