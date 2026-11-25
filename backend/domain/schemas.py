"""Pydantic schemas for API requests, responses, and data validation."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.domain.enums import (
    AnalysisStatus,
    AnalysisType,
    AnnotationType,
    DatasetStatus,
    DeploymentTarget,
    FeedbackType,
    GrowthStageEnum,
    MediaType,
    ModelStatus,
    SeverityLevel,
    TrainingStatus,
    UserRole,
    WeatherAlertSeverity,
)

# ---------------------------------------------------------------------------
# Common / Generic
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


# ---------------------------------------------------------------------------
# Auth / Users
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    preferred_language: str = "ar"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    is_verified: bool
    role_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------------------------
# Farm & FarmLocation
# ---------------------------------------------------------------------------

class FarmLocationBase(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: Optional[float] = None
    region: Optional[str] = None
    country: str = "Yemen"
    governorate: Optional[str] = None


class FarmLocationCreate(FarmLocationBase):
    pass


class FarmLocationResponse(FarmLocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    created_at: datetime


class FarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    area_hectares: Optional[float] = Field(None, ge=0.0)


class FarmCreate(FarmBase):
    location: Optional[FarmLocationCreate] = None


class FarmUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    area_hectares: Optional[float] = None
    location: Optional[FarmLocationCreate] = None


class FarmResponse(FarmBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    location: Optional[FarmLocationResponse] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Crops & Varieties
# ---------------------------------------------------------------------------

class CropVarietyBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None


class CropVarietyCreate(CropVarietyBase):
    pass


class CropVarietyResponse(CropVarietyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    crop_id: uuid.UUID
    created_at: datetime


class GrowthStageBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    stage_order: int
    typical_duration_days: Optional[int] = None
    description: Optional[str] = None


class GrowthStageCreate(GrowthStageBase):
    pass


class GrowthStageResponse(GrowthStageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    crop_id: uuid.UUID
    created_at: datetime


class CropBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    is_supported: bool = False
    icon_url: Optional[str] = None


class CropCreate(CropBase):
    pass


class CropUpdate(BaseModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    is_supported: Optional[bool] = None
    icon_url: Optional[str] = None


class CropResponse(CropBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    varieties: List[CropVarietyResponse] = []
    growth_stages: List[GrowthStageResponse] = []
    created_at: datetime


class FarmCropCycleCreate(BaseModel):
    crop_id: uuid.UUID
    variety_id: Optional[uuid.UUID] = None
    planted_at: Optional[datetime] = None
    current_stage: GrowthStageEnum = GrowthStageEnum.GERMINATION
    notes: Optional[str] = None


class FarmCropCycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    crop_id: uuid.UUID
    variety_id: Optional[uuid.UUID] = None
    planted_at: Optional[datetime] = None
    harvested_at: Optional[datetime] = None
    current_stage: Optional[GrowthStageEnum] = None
    notes: Optional[str] = None
    crop: Optional[CropResponse] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

class MediaUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    media_type: MediaType
    content_type: str
    size_bytes: int
    download_url: str
    farm_id: Optional[uuid.UUID] = None
    crop_id: Optional[uuid.UUID] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Analysis & Predictions
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    media_id: uuid.UUID
    analysis_type: AnalysisType = AnalysisType.DISEASE_DETECTION
    crop_id: Optional[uuid.UUID] = None
    farm_id: Optional[uuid.UUID] = None
    priority: int = 0
    additional_context: Optional[Dict[str, Any]] = None


class AnalysisResultItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str
    confidence: float
    severity: Optional[SeverityLevel] = None
    bounding_box: Optional[Dict[str, Any]] = None
    segmentation_mask_key: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    media_id: uuid.UUID
    analysis_type: AnalysisType
    status: AnalysisStatus
    priority: int
    model_version_id: Optional[uuid.UUID] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    results: List[AnalysisResultItem] = []
    created_at: datetime


# ---------------------------------------------------------------------------
# Diseases & Pests
# ---------------------------------------------------------------------------

class DiseaseBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    symptoms: Optional[Dict[str, Any]] = None
    treatment: Optional[Dict[str, Any]] = None
    prevention: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None


class DiseaseCreate(DiseaseBase):
    pass


class DiseaseResponse(DiseaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class PestBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    lifecycle: Optional[Dict[str, Any]] = None
    damage_type: Optional[str] = None
    control_methods: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None


class PestCreate(PestBase):
    pass


class PestResponse(PestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class CropHealthRecordCreate(BaseModel):
    crop_cycle_id: Optional[uuid.UUID] = None
    analysis_job_id: Optional[uuid.UUID] = None
    disease_id: Optional[uuid.UUID] = None
    severity: SeverityLevel = SeverityLevel.NONE
    confidence_score: Optional[float] = None
    notes: Optional[str] = None


class CropHealthRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    crop_cycle_id: Optional[uuid.UUID] = None
    disease_id: Optional[uuid.UUID] = None
    severity: SeverityLevel
    confidence_score: Optional[float] = None
    notes: Optional[str] = None
    recorded_at: datetime


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

class WeatherObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    precipitation_mm: Optional[float] = None
    pressure_hpa: Optional[float] = None
    cloud_cover_pct: Optional[float] = None
    condition: Optional[str] = None
    observed_at: datetime


class WeatherForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farm_id: uuid.UUID
    forecast_date: datetime
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    precipitation_mm: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    condition: Optional[str] = None
    alert_severity: Optional[WeatherAlertSeverity] = None
    alert_message: Optional[str] = None


class WeatherAlert(BaseModel):
    farm_id: uuid.UUID
    alert_type: str
    severity: WeatherAlertSeverity
    message: str
    message_ar: Optional[str] = None
    issued_at: datetime
    expires_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Pesticides
# ---------------------------------------------------------------------------

class ActiveIngredientBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    chemical_group: Optional[str] = None
    mode_of_action: Optional[str] = None


class ActiveIngredientResponse(ActiveIngredientBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class PesticideLabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    crop_id: Optional[uuid.UUID] = None
    pest_id: Optional[uuid.UUID] = None
    dosage_per_hectare: Optional[str] = None
    dosage_per_liter: Optional[str] = None
    application_method: Optional[str] = None
    safety_interval_days: Optional[int] = None
    max_applications: Optional[int] = None
    notes: Optional[str] = None


class PesticideProductBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    manufacturer: Optional[str] = None
    registration_number: Optional[str] = None
    formulation: Optional[str] = None
    toxicity_class: Optional[str] = None
    target_pests: Optional[Dict[str, Any]] = None
    safety_period_days: Optional[int] = None
    is_restricted: bool = False


class PesticideCreate(PesticideProductBase):
    pass


class PesticideProductResponse(PesticideProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    active_ingredients: List[ActiveIngredientResponse] = []
    labels: List[PesticideLabelResponse] = []
    created_at: datetime


class DosageCalculationRequest(BaseModel):
    pesticide_id: uuid.UUID
    area_hectares: float = Field(..., gt=0.0)
    crop_id: Optional[uuid.UUID] = None
    water_volume_liters: Optional[float] = None


class DosageCalculationResponse(BaseModel):
    pesticide_id: uuid.UUID
    pesticide_name: str
    area_hectares: float
    recommended_product_amount: str
    recommended_water_volume: str
    safety_interval_days: Optional[int] = None
    application_instructions: Optional[str] = None
    safety_warnings: List[str] = []


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    analysis_job_id: uuid.UUID
    feedback_type: FeedbackType
    correct_label: Optional[str] = None
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    analysis_job_id: uuid.UUID
    feedback_type: FeedbackType
    correct_label: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Studio: Datasets, Experiments, Models
# ---------------------------------------------------------------------------

class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    analysis_type: AnalysisType
    tags: Optional[Dict[str, Any]] = None


class DatasetCreate(DatasetBase):
    pass


class DatasetVersionCreate(BaseModel):
    version: str
    split_config: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    version: str
    sample_count: int
    split_config: Optional[Dict[str, Any]] = None
    storage_key: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class DatasetResponse(DatasetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: DatasetStatus
    created_by_id: uuid.UUID
    versions: List[DatasetVersionResponse] = []
    created_at: datetime
    updated_at: datetime


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    analysis_type: AnalysisType
    hypothesis: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    analysis_type: AnalysisType
    hypothesis: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    created_by_id: uuid.UUID
    created_at: datetime


class TrainingRunCreate(BaseModel):
    experiment_id: uuid.UUID
    dataset_version_id: uuid.UUID
    hyperparameters: Optional[Dict[str, Any]] = None


class TrainingRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    experiment_id: uuid.UUID
    dataset_version_id: uuid.UUID
    model_version_id: Optional[uuid.UUID] = None
    status: TrainingStatus
    hyperparameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    version: str
    analysis_type: AnalysisType
    status: ModelStatus
    architecture: Optional[str] = None
    framework: Optional[str] = None
    artifact_key: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    input_shape: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class ModelDeploymentRequest(BaseModel):
    target: DeploymentTarget = DeploymentTarget.SERVER
    config: Optional[Dict[str, Any]] = None


class ModelDeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_version_id: uuid.UUID
    target: DeploymentTarget
    is_active: bool
    deployed_by_id: uuid.UUID
    deployed_at: datetime
    rolled_back_at: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
