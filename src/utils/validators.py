"""
Data validation utilities for Turkish Dream SFT Optimizer.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataValidator:
    """Utility class for data validation."""

    @staticmethod
    def validate_input_data(data: Any) -> bool:
        """
        Validate input data structure.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, list):
            logger.error("Input data must be a list")
            return False

        if len(data) == 0:
            logger.error("Input data is empty")
            return False

        # Check first few records for basic structure
        sample_size = min(5, len(data))
        for i, record in enumerate(data[:sample_size]):
            if not isinstance(record, dict):
                logger.error(f"Record {i} is not a dictionary")
                return False

        logger.info(f"Input data validation passed: {len(data)} records")
        return True

    @staticmethod
    def validate_processed_record(record: Dict[str, Any]) -> bool:
        """
        Validate a processed record.

        Args:
            record: Processed record to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["cleaned_content", "dream_symbol"]

        for field in required_fields:
            if field not in record:
                logger.warning(f"Missing required field: {field}")
                return False

            if not record[field]:
                logger.warning(f"Empty required field: {field}")
                return False

        return True

    @staticmethod
    def validate_sft_records(records: List[Dict[str, Any]], format_type: str) -> bool:
        """
        Validate SFT formatted records.

        Args:
            records: SFT formatted records
            format_type: 'openai' or 'cohere'

        Returns:
            True if valid, False otherwise
        """
        if not records:
            logger.error("No SFT records to validate")
            return False

        sample_size = min(3, len(records))

        for i, record in enumerate(records[:sample_size]):
            if format_type == "openai":
                if "messages" not in record:
                    logger.error(f"OpenAI record {i} missing 'messages' field")
                    return False

                messages = record["messages"]
                if not isinstance(messages, list) or len(messages) < 2:
                    logger.error(f"OpenAI record {i} has invalid messages structure")
                    return False

            elif format_type == "cohere":
                if "prompt" not in record or "completion" not in record:
                    logger.error(f"Cohere record {i} missing required fields")
                    return False

        logger.info(
            f"SFT {format_type} format validation passed: {len(records)} records"
        )
        return True

    @staticmethod
    def get_data_quality_score(records: List[Dict[str, Any]]) -> float:
        """
        Calculate overall data quality score.

        Args:
            records: Processed records

        Returns:
            Quality score between 0 and 1
        """
        if not records:
            return 0.0

        total_score = 0.0
        valid_records = 0

        for record in records:
            score = 0.0

            # Content length score
            content = record.get("cleaned_content", "")
            if len(content) > 100:
                score += 0.3
            elif len(content) > 50:
                score += 0.2
            elif len(content) > 20:
                score += 0.1

            # Dream symbol score
            if record.get("dream_symbol"):
                score += 0.3

            # Tags score
            tags = record.get("tags", [])
            if tags and len(tags) > 0:
                score += 0.2

            # Cultural context score
            if "İslam" in content or "Türk" in content or "rüya" in content:
                score += 0.2

            total_score += score
            valid_records += 1

        if valid_records == 0:
            return 0.0

        return total_score / valid_records
