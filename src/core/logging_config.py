"""Structured logging configuration."""

import json
import logging
import sys
from typing import Any

import structlog

from .config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)  # type: ignore

        return json.dumps(log_data)


def setup_logging() -> None:
    """Initialize structured logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure standard logging
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(message)s",
    )

    if settings.log_format == "json":
        # Configure JSON logging
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())

        root_logger = logging.getLogger()
        root_logger.handlers = [handler]

        # Suppress uvicorn's default logging
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    else:
        # Console format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        for handler in logging.root.handlers:
            handler.setFormatter(formatter)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
