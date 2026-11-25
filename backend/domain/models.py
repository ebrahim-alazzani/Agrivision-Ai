"""SQLAlchemy ORM models for the AgriVision AI platform."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

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
from backend.infrastructure.database import Base

# ---------------------------------------------------------------------------
# Association tables
# ---------------------------------------------------------------------------

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True),
)

disease_crops = Table(
    "disease_crops",
    Base.metadata,
    Column("disease_id", UUID(as_uuid=True), ForeignKey("diseases.id"), primary_key=True),
    Column("crop_id", UUID(as_uuid=True), ForeignKey("crops.id"), primary_key=True),
)

pest_crops = Table(
    "pest_crops",
    Base.metadata,
    Column("pest_id", UUID(as_uuid=True), ForeignKey("pests.id"), primary_key=True),
    Column("crop_id", UUID(as_uuid=True), ForeignKey("crops.id"), primary_key=True),
)

pesticide_active_ingredients = Table(
    "pesticide_active_ingredients",
    Base.metadata,
    Column(
        "pesticide_id",
        UUID(as_uuid=True),
        ForeignKey("pesticide_products.id"),
        primary_key=True,
    ),
    Column(
        "ingredient_id",
        UUID(as_uuid=True),
        ForeignKey("active_ingredients.id"),
        primary_key=True,
    ),
)


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------

class TimestampMixin:
    """Add created_at / updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Auth & Users
# ---------------------------------------------------------------------------

class Permission(TimestampMixin, Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    permissions: Mapped[List[Permission]] = relationship(
        secondary=role_permissions, back_populates="roles"
    )
    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id")
    )
    preferred_language: Mapped[str] = mapped_column(String(10), default="ar")

    role: Mapped[Optional[Role]] = relationship(back_populates="users")
    farm_memberships: Mapped[List["FarmMember"]] = relationship(back_populates="user")
    analysis_jobs: Mapped[List["AnalysisJob"]] = relationship(back_populates="user")
    feedback_records: Mapped[List["FeedbackRecord"]] = relationship(back_populates="user")


# ---------------------------------------------------------------------------
# Farm
# ---------------------------------------------------------------------------

class Farm(TimestampMixin, Base):
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    area_hectares: Mapped[Optional[float]] = mapped_column(Float)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    location: Mapped[Optional["FarmLocation"]] = relationship(
        back_populates="farm", uselist=False, cascade="all, delete-orphan"
    )
    members: Mapped[List["FarmMember"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )
    crop_cycles: Mapped[List["FarmCropCycle"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )
    health_records: Mapped[List["CropHealthRecord"]] = relationship(back_populates="farm")
    weather_observations: Mapped[List["WeatherObservation"]] = relationship(back_populates="farm")


class FarmLocation(TimestampMixin, Base):
    __tablename__ = "farm_locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), unique=True, nullable=False
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude_m: Mapped[Optional[float]] = mapped_column(Float)
    region: Mapped[Optional[str]] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(100), default="Yemen")
    governorate: Mapped[Optional[str]] = mapped_column(String(200))

    farm: Mapped[Farm] = relationship(back_populates="location")


class FarmMember(TimestampMixin, Base):
    __tablename__ = "farm_members"
    __table_args__ = (UniqueConstraint("farm_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="member")

    farm: Mapped[Farm] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="farm_memberships")


# ---------------------------------------------------------------------------
# Crops
# ---------------------------------------------------------------------------

class Crop(TimestampMixin, Base):
    __tablename__ = "crops"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(200))
    scientific_name: Mapped[Optional[str]] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_ar: Mapped[Optional[str]] = mapped_column(Text)
    is_supported: Mapped[bool] = mapped_column(Boolean, default=False)
    icon_url: Mapped[Optional[str]] = mapped_column(String(500))

    varieties: Mapped[List["CropVariety"]] = relationship(
        back_populates="crop", cascade="all, delete-orphan"
    )
    diseases: Mapped[List["Disease"]] = relationship(
        secondary=disease_crops, back_populates="crops"
    )
    pests: Mapped[List["Pest"]] = relationship(secondary=pest_crops, back_populates="crops")
    growth_stages: Mapped[List["GrowthStage"]] = relationship(
        back_populates="crop", cascade="all, delete-orphan"
    )


class CropVariety(TimestampMixin, Base):
    __tablename__ = "crop_varieties"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(200))
    characteristics: Mapped[Optional[dict]] = mapped_column(JSON)

    crop: Mapped[Crop] = relationship(back_populates="varieties")


class GrowthStage(TimestampMixin, Base):
    __tablename__ = "growth_stages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(100))
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    typical_duration_days: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)

    crop: Mapped[Crop] = relationship(back_populates="growth_stages")


class FarmCropCycle(TimestampMixin, Base):
    __tablename__ = "farm_crop_cycles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False
    )
    variety_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crop_varieties.id")
    )
    planted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    harvested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_stage: Mapped[Optional[str]] = mapped_column(
        Enum(GrowthStageEnum), default=GrowthStageEnum.GERMINATION
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)

    farm: Mapped[Farm] = relationship(back_populates="crop_cycles")
    crop: Mapped[Crop] = relationship()
    variety: Mapped[Optional[CropVariety]] = relationship()


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

class MediaAsset(TimestampMixin, Base):
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    media_type: Mapped[str] = mapped_column(Enum(MediaType), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)
    farm_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id")
    )
    crop_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crops.id")
    )
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)


# ---------------------------------------------------------------------------
# Observations & Health
# ---------------------------------------------------------------------------

class Observation(TimestampMixin, Base):
    __tablename__ = "observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    observer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    observation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    media_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media_assets.id")
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CropHealthRecord(TimestampMixin, Base):
    __tablename__ = "crop_health_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    crop_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farm_crop_cycles.id")
    )
    analysis_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_jobs.id")
    )
    severity: Mapped[str] = mapped_column(Enum(SeverityLevel), default=SeverityLevel.NONE)
    disease_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("diseases.id")
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    farm: Mapped[Farm] = relationship(back_populates="health_records")


class PestObservation(TimestampMixin, Base):
    __tablename__ = "pest_observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    pest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pests.id"), nullable=False
    )
    media_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media_assets.id")
    )
    count: Mapped[Optional[int]] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(Enum(SeverityLevel), default=SeverityLevel.LOW)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

class WeatherObservation(TimestampMixin, Base):
    __tablename__ = "weather_observations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    temperature_c: Mapped[Optional[float]] = mapped_column(Float)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float)
    wind_speed_ms: Mapped[Optional[float]] = mapped_column(Float)
    wind_direction_deg: Mapped[Optional[float]] = mapped_column(Float)
    precipitation_mm: Mapped[Optional[float]] = mapped_column(Float)
    pressure_hpa: Mapped[Optional[float]] = mapped_column(Float)
    cloud_cover_pct: Mapped[Optional[float]] = mapped_column(Float)
    condition: Mapped[Optional[str]] = mapped_column(String(100))
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    farm: Mapped[Farm] = relationship(back_populates="weather_observations")


class WeatherForecast(TimestampMixin, Base):
    __tablename__ = "weather_forecasts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False
    )
    forecast_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temp_min_c: Mapped[Optional[float]] = mapped_column(Float)
    temp_max_c: Mapped[Optional[float]] = mapped_column(Float)
    humidity_pct: Mapped[Optional[float]] = mapped_column(Float)
    precipitation_mm: Mapped[Optional[float]] = mapped_column(Float)
    wind_speed_ms: Mapped[Optional[float]] = mapped_column(Float)
    condition: Mapped[Optional[str]] = mapped_column(String(100))
    alert_severity: Mapped[Optional[str]] = mapped_column(Enum(WeatherAlertSeverity))
    alert_message: Mapped[Optional[str]] = mapped_column(Text)


# ---------------------------------------------------------------------------
# Analysis & AI
# ---------------------------------------------------------------------------

class AnalysisJob(TimestampMixin, Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    media_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False
    )
    analysis_type: Mapped[str] = mapped_column(Enum(AnalysisType), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, default=0)
    model_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_versions.id")
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)

    user: Mapped[User] = relationship(back_populates="analysis_jobs")
    results: Mapped[List["AnalysisResult"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    predictions: Mapped[List["ModelPrediction"]] = relationship(back_populates="job")


class AnalysisResult(TimestampMixin, Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(Enum(SeverityLevel))
    bounding_box: Mapped[Optional[dict]] = mapped_column(JSON)
    segmentation_mask_key: Mapped[Optional[str]] = mapped_column(String(1000))
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON)

    job: Mapped[AnalysisJob] = relationship(back_populates="results")


class ModelVersion(TimestampMixin, Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    analysis_type: Mapped[str] = mapped_column(Enum(AnalysisType), nullable=False)
    status: Mapped[str] = mapped_column(Enum(ModelStatus), default=ModelStatus.DRAFT)
    architecture: Mapped[Optional[str]] = mapped_column(String(200))
    framework: Mapped[Optional[str]] = mapped_column(String(100))
    artifact_key: Mapped[Optional[str]] = mapped_column(String(1000))
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    input_shape: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    deployments: Mapped[List["ModelDeployment"]] = relationship(back_populates="model_version")


class ModelPrediction(TimestampMixin, Base):
    __tablename__ = "model_predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False
    )
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False
    )
    raw_output: Mapped[Optional[dict]] = mapped_column(JSON)
    inference_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    device: Mapped[Optional[str]] = mapped_column(String(50))

    job: Mapped[AnalysisJob] = relationship(back_populates="predictions")


# ---------------------------------------------------------------------------
# Diseases, Pests, Pesticides
# ---------------------------------------------------------------------------

class Disease(TimestampMixin, Base):
    __tablename__ = "diseases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(300))
    scientific_name: Mapped[Optional[str]] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_ar: Mapped[Optional[str]] = mapped_column(Text)
    symptoms: Mapped[Optional[dict]] = mapped_column(JSON)
    treatment: Mapped[Optional[dict]] = mapped_column(JSON)
    prevention: Mapped[Optional[dict]] = mapped_column(JSON)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    crops: Mapped[List[Crop]] = relationship(secondary=disease_crops, back_populates="diseases")


class Pest(TimestampMixin, Base):
    __tablename__ = "pests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(300))
    scientific_name: Mapped[Optional[str]] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_ar: Mapped[Optional[str]] = mapped_column(Text)
    lifecycle: Mapped[Optional[dict]] = mapped_column(JSON)
    damage_type: Mapped[Optional[str]] = mapped_column(String(200))
    control_methods: Mapped[Optional[dict]] = mapped_column(JSON)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    crops: Mapped[List[Crop]] = relationship(secondary=pest_crops, back_populates="pests")


class PesticideProduct(TimestampMixin, Base):
    __tablename__ = "pesticide_products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(300))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(300))
    registration_number: Mapped[Optional[str]] = mapped_column(String(100))
    formulation: Mapped[Optional[str]] = mapped_column(String(200))
    toxicity_class: Mapped[Optional[str]] = mapped_column(String(50))
    target_pests: Mapped[Optional[dict]] = mapped_column(JSON)
    safety_period_days: Mapped[Optional[int]] = mapped_column(Integer)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False)

    active_ingredients: Mapped[List["ActiveIngredient"]] = relationship(
        secondary=pesticide_active_ingredients, back_populates="products"
    )
    labels: Mapped[List["PesticideLabel"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ActiveIngredient(TimestampMixin, Base):
    __tablename__ = "active_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    name_ar: Mapped[Optional[str]] = mapped_column(String(300))
    chemical_group: Mapped[Optional[str]] = mapped_column(String(200))
    mode_of_action: Mapped[Optional[str]] = mapped_column(Text)

    products: Mapped[List[PesticideProduct]] = relationship(
        secondary=pesticide_active_ingredients, back_populates="active_ingredients"
    )


class PesticideLabel(TimestampMixin, Base):
    __tablename__ = "pesticide_labels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pesticide_products.id"), nullable=False
    )
    crop_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crops.id")
    )
    pest_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pests.id")
    )
    dosage_per_hectare: Mapped[Optional[str]] = mapped_column(String(200))
    dosage_per_liter: Mapped[Optional[str]] = mapped_column(String(200))
    application_method: Mapped[Optional[str]] = mapped_column(Text)
    safety_interval_days: Mapped[Optional[int]] = mapped_column(Integer)
    max_applications: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    product: Mapped[PesticideProduct] = relationship(back_populates="labels")


# ---------------------------------------------------------------------------
# AI Studio: Datasets & Training
# ---------------------------------------------------------------------------

class Dataset(TimestampMixin, Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    analysis_type: Mapped[str] = mapped_column(Enum(AnalysisType), nullable=False)
    status: Mapped[str] = mapped_column(Enum(DatasetStatus), default=DatasetStatus.DRAFT)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    tags: Mapped[Optional[dict]] = mapped_column(JSON)

    versions: Mapped[List["DatasetVersion"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class DatasetVersion(TimestampMixin, Base):
    __tablename__ = "dataset_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
    split_config: Mapped[Optional[dict]] = mapped_column(JSON)
    storage_key: Mapped[Optional[str]] = mapped_column(String(1000))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    dataset: Mapped[Dataset] = relationship(back_populates="versions")
    samples: Mapped[List["DatasetSample"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )


class DatasetSample(TimestampMixin, Base):
    __tablename__ = "dataset_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dataset_versions.id"), nullable=False
    )
    media_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("media_assets.id"), nullable=False
    )
    split: Mapped[str] = mapped_column(String(20), default="train")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    version: Mapped[DatasetVersion] = relationship(back_populates="samples")
    annotations: Mapped[List["Annotation"]] = relationship(
        back_populates="sample", cascade="all, delete-orphan"
    )


class Annotation(TimestampMixin, Base):
    __tablename__ = "annotations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dataset_samples.id"), nullable=False
    )
    annotator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    annotation_type: Mapped[str] = mapped_column(Enum(AnnotationType), nullable=False)
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSON)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    sample: Mapped[DatasetSample] = relationship(back_populates="annotations")


class Experiment(TimestampMixin, Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    analysis_type: Mapped[str] = mapped_column(Enum(AnalysisType), nullable=False)
    hypothesis: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[dict]] = mapped_column(JSON)

    training_runs: Mapped[List["TrainingRun"]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class TrainingRun(TimestampMixin, Base):
    __tablename__ = "training_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False
    )
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dataset_versions.id"), nullable=False
    )
    model_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_versions.id")
    )
    status: Mapped[str] = mapped_column(Enum(TrainingStatus), default=TrainingStatus.PENDING)
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSON)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    logs_key: Mapped[Optional[str]] = mapped_column(String(1000))

    experiment: Mapped[Experiment] = relationship(back_populates="training_runs")


class EvaluationReport(TimestampMixin, Base):
    __tablename__ = "evaluation_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_runs.id"), nullable=False
    )
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    confusion_matrix: Mapped[Optional[dict]] = mapped_column(JSON)
    per_class_metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    report_key: Mapped[Optional[str]] = mapped_column(String(1000))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class ModelDeployment(TimestampMixin, Base):
    __tablename__ = "model_deployments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False
    )
    target: Mapped[str] = mapped_column(Enum(DeploymentTarget), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deployed_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rolled_back_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    config: Mapped[Optional[dict]] = mapped_column(JSON)

    model_version: Mapped[ModelVersion] = relationship(back_populates="deployments")


# ---------------------------------------------------------------------------
# Feedback & Confidence
# ---------------------------------------------------------------------------

class FeedbackRecord(TimestampMixin, Base):
    __tablename__ = "feedback_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False
    )
    feedback_type: Mapped[str] = mapped_column(Enum(FeedbackType), nullable=False)
    correct_label: Mapped[Optional[str]] = mapped_column(String(300))
    comment: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="feedback_records")


class ConfidenceRecord(TimestampMixin, Base):
    __tablename__ = "confidence_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False
    )
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False
    )
    predicted_label: Mapped[str] = mapped_column(String(300), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    calibrated_score: Mapped[Optional[float]] = mapped_column(Float)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
