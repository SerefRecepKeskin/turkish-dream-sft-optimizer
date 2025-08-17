"""
File handling utilities for Turkish Dream SFT Optimizer.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class FileHandler:
    """Utility class for file operations."""

    @staticmethod
    def load_json(file_path: str) -> Any:
        """
        Load JSON data from file.

        Args:
            file_path: Path to JSON file

        Returns:
            Loaded JSON data
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded data from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
            raise

    @staticmethod
    def save_json(data: Any, file_path: str, indent: int = 2) -> None:
        """
        Save data to JSON file.

        Args:
            data: Data to save
            file_path: Output file path
            indent: JSON indentation
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            logger.info(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            raise

    @staticmethod
    def save_jsonl(records: List[Dict[str, Any]], file_path: str) -> None:
        """
        Save records to JSONL file.

        Args:
            records: List of records to save
            file_path: Output file path
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.info(f"Saved {len(records)} records to {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSONL to {file_path}: {e}")
            raise

    @staticmethod
    def ensure_directory(dir_path: str) -> Path:
        """
        Ensure directory exists.

        Args:
            dir_path: Directory path

        Returns:
            Path object
        """
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
