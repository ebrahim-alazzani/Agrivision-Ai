"""AgriVision AI Backend FastAPI Application Factory and Entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.v1.router import api_router
from backend.infrastructure.config import get_settings
from backend.infrastructure.database import Base, engine
from backend.infrastructure.storage import S3Storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agrivision")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown routines."""
    logger.info("Initializing AgriVision AI backend services...")

    # Ensure database schema exists (for development / testing)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas verified.")

    # Ensure MinIO / S3 bucket exists
    try:
        storage = S3Storage()
        storage.ensure_bucket()
        logger.info(f"S3/MinIO bucket '{settings.s3_bucket_name}' verified.")
    except Exception as e:
        logger.warning(f"Could not connect to S3/MinIO at startup: {e}")

    yield

    logger.info("Shutting down AgriVision AI backend...")
    await engine.dispose()
    logger.info("Database engine connections closed.")


def create_application() -> FastAPI:
    """Create and configure FastAPI application instance."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AgriVision AI — Enterprise Agricultural Intelligence & Diagnostic Platform",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoints
    @app.get("/health", tags=["System"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    # Mount v1 API
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
