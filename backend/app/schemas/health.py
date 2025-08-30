"""Health check schemas."""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status values."""
    OK = "ok"
    ERROR = "error"
    DEGRADED = "degraded"


class HealthCheck(BaseModel):
    """Health check response model."""
    status: HealthStatus = Field(..., description="Overall health status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the check")
    checks: Optional[Dict[str, Dict[str, str]]] = Field(
        None, description="Detailed health check results"
    )


class HealthCheckResponse(BaseModel):
    """Health check response with details."""
    status: str = Field(..., description="Overall status")
    checks: List[Dict[str, str]] = Field(
        default_factory=list, description="List of health check results"
    )


class DatabaseStatus(BaseModel):
    """Database status response model."""
    status: str = Field(..., description="Database connection status")
    version: Optional[str] = Field(None, description="Database version")
    details: Optional[Dict[str, str]] = Field(
        None, description="Additional database details"
    )


class ServiceHealth(BaseModel):
    """Service health status."""
    name: str = Field(..., description="Service name")
    status: HealthStatus = Field(..., description="Service status")
    response_time: Optional[float] = Field(
        None, description="Response time in milliseconds"
    )
    error: Optional[str] = Field(None, description="Error details if status is not OK")
