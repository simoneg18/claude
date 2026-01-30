"""Logging configuration for TCG Monitor."""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """
    Configure logging to file and console.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_path / "monitor.log", encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)
