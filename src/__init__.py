"""
Turkish Dream SFT Optimizer - High-performance dream interpretation dataset optimizer.

A comprehensive data processing pipeline for converting Turkish dream interpretation
datasets into optimized SFT training formats for OpenAI and Cohere platforms.
"""

__version__ = "1.0.0"
__author__ = "Seref Recep Keskin"

from .core import (
    DreamDataProcessor,
    ParallelDreamProcessor,
    PerformanceOptimizer,
    QualityChecker,
    create_parallel_processor,
)
from .formatters import BaseSFTFormatter, CohereFormatter, OpenAIFormatter
from .utils import DataValidator, FileHandler, setup_logger

__all__ = [
    # Core modules
    "DreamDataProcessor",
    "ParallelDreamProcessor",
    "PerformanceOptimizer",
    "create_parallel_processor",
    "QualityChecker",
    # Formatters
    "BaseSFTFormatter",
    "OpenAIFormatter",
    "CohereFormatter",
    # Utils
    "FileHandler",
    "setup_logger",
    "DataValidator",
]
