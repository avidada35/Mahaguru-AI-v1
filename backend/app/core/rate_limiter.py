"""Rate limiting configuration for Mahaguru AI."""
from typing import Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    headers_enabled=True,
)

# Rate limit configurations
RATE_LIMITS = {
    "public": "100/minute",
    "auth": "10/minute",
    "ai_search": "30/minute",
    "ai_answer": "10/minute",
    "default": "1000/hour",
}

def get_rate_limit_key(
    request: Request,
    key: Optional[str] = None,
    rate_limit: Optional[str] = None,
) -> str:
    """Get rate limit key based on the request and endpoint.
    
    Args:
        request: The incoming request
        key: Optional custom key for the rate limit
        rate_limit: Optional custom rate limit string (e.g., "10/minute")
    
    Returns:
        str: The rate limit key
    """
    if key:
        return f"{key}:{request.client.host}"
    
    # Default to endpoint-based rate limiting
    endpoint = request.url.path
    
    # Apply specific rate limits based on endpoint
    if endpoint.startswith("/api/v1/auth"):
        return f"auth:{request.client.host}"
    elif endpoint == "/api/v1/ai/search":
        return f"ai_search:{request.client.host}"
    elif endpoint == "/api/v1/ai/answer":
        return f"ai_answer:{request.client.host}"
    
    return f"default:{request.client.host}"

def get_rate_limit(limit_key: str) -> str:
    """Get the rate limit for a given key.
    
    Args:
        limit_key: The rate limit key
    
    Returns:
        str: The rate limit string (e.g., "10/minute")
    """
    # Extract the rate limit type from the key
    limit_type = limit_key.split(":")[0]
    return RATE_LIMITS.get(limit_type, RATE_LIMITS["default"])

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> None:
    """Handle rate limit exceeded errors."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "message": "Rate limit exceeded",
            "retry_after": f"{exc.detail.retry_after} seconds",
        },
        headers={"Retry-After": str(exc.detail.retry_after)},
    )

def setup_rate_limiting(app: FastAPI) -> None:
    """Set up rate limiting for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Initialize the limiter
    app.state.limiter = limiter
    
    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    # Add rate limiting middleware
    app.add_middleware(SlowAPIMiddleware)
    
    # Apply rate limits to all endpoints by default
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Skip rate limiting for certain paths
        if request.url.path in ["/healthz", "/readyz", "/metrics"]:
            return await call_next(request)
            
        # Get rate limit key and limit
        limit_key = get_rate_limit_key(request)
        limit = get_rate_limit(limit_key)
        
        # Apply rate limit
        with limiter.limit(limit, key_func=lambda: limit_key):
            return await call_next(request)
