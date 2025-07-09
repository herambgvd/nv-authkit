"""
FastAPI User Management System - Main Application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_db, close_db, check_db_health
from app.core.exceptions import UserManagementException
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.roles import router as roles_router
from app.api.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting FastAPI User Management System...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Check database health
        db_healthy = await check_db_health()
        if db_healthy:
            logger.info("Database health check passed")
        else:
            logger.warning("Database health check failed")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down FastAPI User Management System...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="A production-ready user management system built with FastAPI",
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
    openapi_url="/openapi.json" if settings.app.debug else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app.debug else [settings.app.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (for production)
if not settings.app.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with your actual domain
    )


# Global exception handler
@app.exception_handler(UserManagementException)
async def user_management_exception_handler(request: Request, exc: UserManagementException):
    """Handle custom user management exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.app.api_prefix)
app.include_router(users_router, prefix=settings.app.api_prefix)
app.include_router(roles_router, prefix=settings.app.api_prefix)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app.name}",
        "version": settings.app.version,
        "docs_url": "/docs" if settings.app.debug else "Disabled in production",
        "health_check": "/health"
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.app.debug,
        log_level="info"
    )