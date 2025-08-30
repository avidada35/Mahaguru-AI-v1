"""API package initialization."""
from fastapi import APIRouter

from app.api.v1.api import api_router as api_v1_router

# Create main API router
api_router = APIRouter()

# Include API version 1 router
api_router.include_router(api_v1_router, prefix=api_v1_router.prefix)
