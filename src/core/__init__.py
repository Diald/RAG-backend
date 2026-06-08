"""Core module - shared configurations, logging, and utilities."""

from .config import Settings
from .logging_config import setup_logging

__all__ = ["Settings", "setup_logging"]
