"""Main FastAPI Application Entrypoint."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("task_management_api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for startup and shutdown procedures."""
    logger.info("Starting up Task Management REST API...")
    logger.info("Environment: %s", settings.ENVIRONMENT)
    yield
    logger.info("Shutting down Task Management REST API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "A production-grade, secure, and resume-worthy Task Management REST API built with "
        "FastAPI, SQLAlchemy 2.0, PostgreSQL/SQLite, Alembic migrations, and JWT Authentication."
    ),
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Custom exception handlers for clean, professional error formatting
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Format Pydantic validation errors into clean, structured responses."""
    errors = []
    for err in exc.errors():
        location = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": location,
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed.",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler to avoid exposing raw stack traces in production."""
    logger.error("Unhandled server exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


# Health check endpoints
@app.get("/", tags=["Health Check"], summary="Root status check")
def root() -> dict:
    """Root health check returning service metadata."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health Check"], summary="Liveness probe")
def health_check() -> dict:
    """Liveness probe for orchestration platforms (Kubernetes / Docker / Render)."""
    return {"status": "healthy"}


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
