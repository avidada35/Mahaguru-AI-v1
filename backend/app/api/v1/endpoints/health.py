"""Health check endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.session import get_db
from app.schemas.health import HealthCheck, HealthStatus

router = APIRouter()


@router.get("/healthz", response_model=HealthCheck, tags=["health"])
async def health_check() -> HealthCheck:
    """Basic health check endpoint.
    
    This endpoint performs a basic application health check without external dependencies.
    """
    return HealthCheck(status=HealthStatus.OK)


@router.get(
    "/readyz",
    response_model=HealthCheck,
    responses={
        200: {"description": "Application is ready to handle requests"},
        503: {"description": "Application is not ready"},
    },
    tags=["health"],
)
async def readiness_check(db: AsyncSession = Depends(get_db)) -> HealthCheck:
    """Readiness check endpoint.
    
    This endpoint checks if the application is ready to handle requests by verifying:
    - Database connectivity
    - Any other critical dependencies
    """
    try:
        # Check database connectivity
        await db.execute("SELECT 1")
        
        # Add additional checks here (e.g., Redis, external services)
        
        return HealthCheck(status=HealthStatus.OK)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}",
        )


@router.get(
    "/metrics",
    responses={
        200: {"description": "Prometheus metrics"},
    },
    tags=["metrics"],
)
async def metrics() -> str:
    """Prometheus metrics endpoint.
    
    This endpoint exposes application metrics in Prometheus format.
    """
    from app.core.metrics import get_metrics
    from fastapi.responses import Response
    
    return Response(
        content=get_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
