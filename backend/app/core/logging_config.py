"""Structured logging configuration for Mahaguru AI."""
import json
import logging
import logging.config
import sys
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.core.config import settings


class LogConfig(BaseModel):
    """Logging configuration to be set for the server."""
    LOGGER_NAME: str = "mahaguru"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    JSON_LOGS: bool = settings.ENVIRONMENT != "local"

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": """
                asctime: %(asctime)s
                level: %(levelname)s
                name: %(name)s
                message: %(message)s
                module: %(module)s
                funcName: %(funcName)s
                lineno: %(lineno)d
            """,
        },
    }
    handlers: Dict[str, Dict[str, Any]] = {
        "default": {
            "formatter": "json" if JSON_LOGS else "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    }
    loggers: Dict[str, Dict[str, Any]] = {
        "": {
            "handlers": ["default"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
    }


def configure_logging() -> None:
    """Configure logging with the specified settings."""
    config = LogConfig()
    logging.config.dictConfig(config.dict())
    
    # Set up root logger
    logger = logging.getLogger(config.LOGGER_NAME)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Add request ID filter
    logging.getLogger("uvicorn.access").addFilter(RequestIdFilter())


class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        from fastapi import Request
        from starlette.middleware.base import BaseHTTPMiddleware
        
        request: Optional[Request] = getattr(record, "request", None)
        if request:
            record.request_id = request.state.request_id
        return True


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "props"):
            log_record.update(record.props)
            
        return json.dumps(log_record, ensure_ascii=False)
