"""Structured logging utilities."""

import logging
import sys
from typing import Optional

# Try to use rich for colored output
try:
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get a configured logger.

    Args:
        name: Logger name
        level: Log level (INFO, DEBUG, WARNING, ERROR)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, level))

        if RICH_AVAILABLE:
            handler = RichHandler(rich_tracebacks=True)
        else:
            handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def setup_logging(level: str = "INFO", use_rich: bool = True) -> None:
    """Setup global logging configuration.

    Args:
        level: Log level
        use_rich: Use rich handler if available
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Clear existing handlers
    root_logger.handlers.clear()

    if use_rich and RICH_AVAILABLE:
        handler = RichHandler(rich_tracebacks=True)
    else:
        handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
