"""Metrics configuration for Mahaguru AI."""
from typing import Callable, Optional

from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings

# Application Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5],
)
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
    multiprocess_mode="livesum",
)

# Database Metrics
DB_QUERIES_TOTAL = Counter(
    "db_queries_total",
    "Total number of database queries",
    ["model", "operation"],
)
DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["model", "operation"],
)

# AI Model Metrics
AI_REQUESTS_TOTAL = Counter(
    "ai_requests_total",
    "Total number of AI model requests",
    ["model", "endpoint"],
)
AI_REQUEST_DURATION = Histogram(
    "ai_request_duration_seconds",
    "AI model request duration in seconds",
    ["model", "endpoint"],
)
AI_REQUEST_TOKENS = Counter(
    "ai_request_tokens_total",
    "Total number of tokens processed by AI models",
    ["model", "endpoint", "type"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP request metrics."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip metrics endpoint to avoid noise
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Track request in progress
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        # Track request latency
        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
            try:
                response = await call_next(request)
                status_code = response.status_code
                return response
            except Exception as e:
                status_code = 500
                raise
            finally:
                # Always record the request count, even if an exception occurred
                REQUEST_COUNT.labels(
                    method=method, endpoint=endpoint, http_status=status_code
                ).inc()
                REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()


def get_metrics() -> bytes:
    """Get the current metrics in Prometheus format."""
    return generate_latest(REGISTRY)


def track_db_query(
    model: str, operation: str
) -> Callable:
    """Decorator to track database queries.
    
    Args:
        model: The model being queried
        operation: The operation being performed (e.g., 'select', 'insert', 'update', 'delete')
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            DB_QUERIES_TOTAL.labels(model=model, operation=operation).inc()
            with DB_QUERY_DURATION.labels(model=model, operation=operation).time():
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def track_ai_request(model: str, endpoint: str):
    """Decorator to track AI model requests.
    
    Args:
        model: The AI model being called
        endpoint: The API endpoint making the request
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            AI_REQUESTS_TOTAL.labels(model=model, endpoint=endpoint).inc()
            with AI_REQUEST_DURATION.labels(model=model, endpoint=endpoint).time():
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def record_ai_tokens(model: str, endpoint: str, prompt_tokens: int, completion_tokens: int):
    """Record token usage for AI requests.
    
    Args:
        model: The AI model
        endpoint: The API endpoint
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
    """
    AI_REQUEST_TOKENS.labels(model=model, endpoint=endpoint, type="prompt").inc(prompt_tokens)
    AI_REQUEST_TOKENS.labels(model=model, endpoint=endpoint, type="completion").inc(completion_tokens)
