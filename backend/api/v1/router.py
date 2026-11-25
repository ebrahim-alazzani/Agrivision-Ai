"""Main API v1 router consolidating all domain sub-routers."""

from fastapi import APIRouter

from backend.api.v1.endpoints import (
    analysis,
    auth,
    crops,
    farms,
    feedback,
    knowledge,
    media,
    pesticides,
    pests,
    plant_health,
    studio_datasets,
    studio_models,
    studio_training,
    weather,
)

api_router = APIRouter()

# Core Farmers & Agronomists API
api_router.include_router(auth.router)
api_router.include_router(farms.router)
api_router.include_router(crops.router)
api_router.include_router(media.router)
api_router.include_router(analysis.router)
api_router.include_router(plant_health.router)
api_router.include_router(pests.router)
api_router.include_router(weather.router)
api_router.include_router(pesticides.router)
api_router.include_router(feedback.router)
api_router.include_router(knowledge.router)

# AI Studio API
api_router.include_router(studio_datasets.router)
api_router.include_router(studio_training.router)
api_router.include_router(studio_models.router)
