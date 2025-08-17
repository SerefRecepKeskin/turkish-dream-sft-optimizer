"""
Logger setup utilities for Turkish Dream SFT Optimizer.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_log_level(level_str: str) -> int:
    """Convert string log level to logging constant."""
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_mapping.get(level_str.upper(), logging.INFO)


def setup_logger(
    name: str = __name__,
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    Setup logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level (if None, will use env config)
        log_file: Optional log file path
        console_output: Whether to output to console

    Returns:
        Configured logger
    """
    # Import here to avoid circular imports
    try:
        from .env_config import env_config

        if level is None:
            level = get_log_level(env_config.log_level)
    except ImportError:
        level = level or logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
