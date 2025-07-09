"""
Health check API endpoints.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, check_db_health
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the health status of the application and its dependencies."
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""

    # Check database connectivity
    db_healthy = await check_db_health()

    # Check Redis connectivity (if using Redis)
    redis_healthy = True  # Implement Redis health check if needed

    # Overall health status
    healthy = db_healthy and redis_healthy

    health_data = {
        "status": "healthy" if healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app.version,
        "environment": "development" if settings.app.debug else "production",
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy"
        }
    }

    if not healthy:
        # Return 503 Service Unavailable if unhealthy
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        status_code = status.HTTP_200_OK

    return health_data


@router.get(
    "/health/db",
    status_code=status.HTTP_200_OK,
    summary="Database health check",
    description="Check the health status of the database connection."
)
async def database_health_check():
    """Database-specific health check."""
    db_healthy = await check_db_health()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "database"
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the application is ready to serve requests."
)
async def readiness_check():
    """Readiness check for Kubernetes deployments."""
    # Check all critical dependencies
    db_healthy = await check_db_health()

    ready = db_healthy

    return {
        "status": "ready" if ready else "not ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Check if the application is alive and running."
)
async def liveness_check():
    """Liveness check for Kubernetes deployments."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }