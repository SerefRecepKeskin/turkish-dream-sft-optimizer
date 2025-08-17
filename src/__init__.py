"""
Turkish Dream SFT Optimizer Package

A comprehensive data processing pipeline for converting Turkish dream interpretation
datasets into optimized SFT training formats for OpenAI and Cohere platforms.

Modules:
    data_processor: Data cleaning and validation
    formatters: SFT format conversion (OpenAI & Cohere)
    quality_checker: Quality analysis and metrics
"""

__version__ = "1.0.0"
__author__ = "Turkish Dream SFT Team"
__email__ = "support@turkishdream-sft.com"

from .data_processor import DreamDataProcessor
from .formatters import CohereFormatter, DataAugmenter, OpenAIFormatter
from .quality_checker import QualityChecker

__all__ = [
    "DreamDataProcessor",
    "OpenAIFormatter",
    "CohereFormatter",
    "DataAugmenter",
    "QualityChecker",
]
