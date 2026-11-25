"""Domain enumerations for the AgriVision AI platform."""

import enum


class UserRole(str, enum.Enum):
    """User roles within the system."""
    ADMIN = "admin"
    AGRONOMIST = "agronomist"
    FARMER = "farmer"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class AnalysisStatus(str, enum.Enum):
    """Status of an analysis job."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(str, enum.Enum):
    """Severity level for diseases and pest infestations."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class GrowthStageEnum(str, enum.Enum):
    """Growth stages of a crop."""
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    RIPENING = "ripening"
    HARVEST = "harvest"
    DORMANT = "dormant"


class MediaType(str, enum.Enum):
    """Type of uploaded media."""
    IMAGE = "image"
    VIDEO = "video"


class AnalysisType(str, enum.Enum):
    """Types of AI analysis."""
    DISEASE_DETECTION = "disease_detection"
    PEST_DETECTION = "pest_detection"
    CROP_MONITORING = "crop_monitoring"
    WEATHER_ANALYSIS = "weather_analysis"
    PESTICIDE_LABEL = "pesticide_label"


class ModelStatus(str, enum.Enum):
    """Status of a deployed model."""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATING = "validating"
    READY = "ready"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TrainingStatus(str, enum.Enum):
    """Status of a training run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DatasetStatus(str, enum.Enum):
    """Status of a dataset."""
    DRAFT = "draft"
    COLLECTING = "collecting"
    ANNOTATING = "annotating"
    REVIEWING = "reviewing"
    READY = "ready"
    ARCHIVED = "archived"


class AnnotationType(str, enum.Enum):
    """Type of annotation."""
    CLASSIFICATION = "classification"
    BOUNDING_BOX = "bounding_box"
    SEGMENTATION = "segmentation"
    POLYGON = "polygon"
    KEYPOINT = "keypoint"


class WeatherAlertSeverity(str, enum.Enum):
    """Weather alert severity levels."""
    ADVISORY = "advisory"
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"


class FeedbackType(str, enum.Enum):
    """Types of user feedback on analysis results."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIALLY_CORRECT = "partially_correct"
    UNSURE = "unsure"


class DeploymentTarget(str, enum.Enum):
    """Where a model can be deployed."""
    SERVER = "server"
    MOBILE = "mobile"
    EDGE = "edge"
