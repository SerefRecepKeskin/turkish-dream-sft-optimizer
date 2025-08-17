"""
Environment configuration utilities for Turkish Dream SFT Optimizer.
"""

import os
from pathlib import Path
from typing import Any, Optional, Union

try:
    from dotenv import load_dotenv

    # Load .env file from project root
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    # python-dotenv not available, continue without it
    pass


def get_env_var(
    key: str, default: Any = None, var_type: type = str, required: bool = False
) -> Any:
    """
    Get environment variable with type conversion and validation.

    Args:
        key: Environment variable name
        default: Default value if not found
        var_type: Type to convert the value to
        required: Whether the variable is required

    Returns:
        Converted environment variable value or default

    Raises:
        ValueError: If required variable is missing or conversion fails
    """
    value = os.getenv(key)

    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return default

    # Handle empty string values
    if value.strip() == "":
        return default

    try:
        if var_type == bool:
            return value.lower() in ("true", "1", "yes", "on")
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        else:
            return value
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Cannot convert environment variable '{key}' value '{value}' to {var_type.__name__}: {e}"
        )


class EnvConfig:
    """Environment configuration manager."""

    def __init__(self):
        """Initialize with environment variables."""
        # Processing configuration
        self.min_content_length = get_env_var("MIN_CONTENT_LENGTH", 100, int)
        self.max_content_length = get_env_var("MAX_CONTENT_LENGTH", 5000, int)
        self.min_cultural_indicators = get_env_var("MIN_CULTURAL_INDICATORS", 3, int)

        # Parallel processing configuration
        self.max_workers = get_env_var("MAX_WORKERS", None, int)
        self.chunk_size = get_env_var("CHUNK_SIZE", None, int)

        # Output configuration
        self.output_dir = get_env_var("OUTPUT_DIR", "output", str)
        self.save_processed_data = get_env_var("SAVE_PROCESSED_DATA", True, bool)
        self.save_openai_format = get_env_var("SAVE_OPENAI_FORMAT", True, bool)
        self.save_cohere_format = get_env_var("SAVE_COHERE_FORMAT", True, bool)
        self.save_quality_report = get_env_var("SAVE_QUALITY_REPORT", True, bool)

        # Logging configuration
        self.log_level = get_env_var("LOG_LEVEL", "INFO", str)
        self.log_file = get_env_var("LOG_FILE", "processing.log", str)

        # Quality assurance
        self.min_quality_score = get_env_var("MIN_QUALITY_SCORE", 0.7, float)
        self.enable_strict_validation = get_env_var(
            "ENABLE_STRICT_VALIDATION", False, bool
        )
        self.max_validation_errors = get_env_var("MAX_VALIDATION_ERRORS", 10, int)


# Global configuration instance
env_config = EnvConfig()
