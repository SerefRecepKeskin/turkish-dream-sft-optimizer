# Veri temizleme modülü
# Turkish Dream SFT Optimizer - Data Processing
"""
Data processing module for Turkish dream interpretation dataset.
Handles cleaning, filtering, and optimization of MongoDB export data.
"""

import html
import logging
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DreamDataProcessor:
    """Process and clean Turkish dream interpretation data for SFT training."""

    def __init__(self, min_content_length: int = 100):
        """
        Initialize the data processor.

        Args:
            min_content_length: Minimum content length for quality filtering
        """
        self.min_content_length = min_content_length
        self.processed_count = 0
        self.filtered_count = 0

        # Compile regex patterns for performance
        self.html_pattern = re.compile(r"<[^>]+>")
        self.whitespace_pattern = re.compile(r"\s+")
        self.seo_noise_pattern = re.compile(
            r"(seo|SEO|amp|AMP|milliyet|Milliyet|pembenar|PembeNar)", re.IGNORECASE
        )

    def clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content and extract meaningful text.

        Args:
            html_content: Raw HTML content from Text field

        Returns:
            Cleaned plain text content
        """
        if not html_content:
            return ""

        try:
            # Use BeautifulSoup for robust HTML parsing
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up whitespace
            text = self.whitespace_pattern.sub(" ", text)
            text = text.strip()

            # Decode HTML entities
            text = html.unescape(text)

            return text

        except Exception as e:
            logger.warning(f"HTML cleaning failed, using regex fallback: {e}")
            # Fallback to regex-based cleaning
            text = self.html_pattern.sub("", html_content)
            text = html.unescape(text)
            text = self.whitespace_pattern.sub(" ", text)
            return text.strip()

    def extract_dream_symbol(self, title: str) -> str:
        """
        Extract the main dream symbol from title.

        Args:
            title: Article title

        Returns:
            Main dream symbol (e.g., "fare", "yılan")
        """
        if not title:
            return ""

        # Common patterns in Turkish dream interpretation titles
        patterns = [r"Rüyada\s+(\w+)\s+Görmek", r"Rüyada\s+(\w+)", r"(\w+)\s+Görmek"]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                symbol = match.group(1).lower()
                # Filter out common words
                if symbol not in ["ne", "nedir", "anlama", "gelir", "neye"]:
                    return symbol

        return ""

    def clean_tags(self, tags: List[str]) -> List[str]:
        """
        Clean and filter tags for better quality.

        Args:
            tags: List of tags from the record

        Returns:
            Cleaned list of relevant tags
        """
        if not tags:
            return []

        cleaned_tags = []
        for tag in tags:
            if isinstance(tag, str):
                tag = tag.strip().lower()
                # Filter out SEO noise and generic tags
                if (
                    tag
                    and len(tag) > 1
                    and not self.seo_noise_pattern.search(tag)
                    and tag not in ["1", "2", "3", "ruya", "rüya"]
                ):
                    cleaned_tags.append(tag)

        return cleaned_tags

    def extract_seo_content(self, properties: List[Dict]) -> Dict[str, str]:
        """
        Extract useful content from SEO properties.

        Args:
            properties: Properties array from MongoDB record

        Returns:
            Dictionary with extracted SEO content
        """
        seo_content = {"seo_title": "", "seo_description": ""}

        if not isinstance(properties, list):
            return seo_content

        for prop in properties:
            if isinstance(prop, dict):
                ix_name = prop.get("IxName", "").lower()
                value = prop.get("Value", "")

                if ix_name == "seotitle" and value:
                    seo_content["seo_title"] = value.strip()
                elif ix_name == "seodescription" and value:
                    seo_content["seo_description"] = value.strip()

        return seo_content

    def validate_record_quality(self, record: Dict[str, Any]) -> bool:
        """
        Validate if a record meets quality standards for training.

        Args:
            record: Processed record dictionary

        Returns:
            True if record meets quality standards
        """
        # Check essential fields
        if not record.get("cleaned_content"):
            return False

        # Check content length
        if len(record["cleaned_content"]) < self.min_content_length:
            return False

        # Check if it has a meaningful dream symbol
        if not record.get("dream_symbol"):
            return False

        # Check for minimum cultural context
        content = record["cleaned_content"].lower()
        turkish_indicators = [
            # Temel rüya kelimeleri
            "rüya",
            "rüyada",
            "rüyası",
            "rüyalar",
            # Görme fiilleri
            "görmek",
            "görür",
            "görenin",
            "gören",
            # Yorum ve anlam kelimeleri
            "yorumlanır",
            "yorumu",
            "yorumlar",
            "delalet",
            "delalet eder",
            "tabir",
            "tabiri",
            "anlamı",
            "anlama gelir",
            "manası",
            "işaret",
            "işareti",
            "alamet",
            "belirtisi",
            # Dini/kültürel terimler
            "hayırlı",
            "hayırsız",
            "müjde",
            "uyarı",
            "bereket",
            "şifa",
            "rahmet",
            "kısmet",
            "nasip",
            "rızık",
            "sevap",
            "günah",
            "haram",
            "helal",
            # Duygusal durumlar
            "sevinç",
            "üzüntü",
            "korku",
            "endişe",
            "huzur",
            "sıkıntı",
            "mutluluk",
            "kaygı",
            # Yaygın rüya yorumu ifadeleri
            "ileride",
            "gelecekte",
            "yakında",
            "başına gelecek",
            "karşılaşacak",
            "yaşayacak",
            "elde edecek",
        ]

        # En az 2 farklı indicator olmalı (daha güvenilir)
        indicator_count = sum(
            1 for indicator in turkish_indicators if indicator in content
        )
        if indicator_count < 2:
            return False

        return True

    def process_single_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single dream interpretation record.

        Args:
            record: Raw MongoDB record

        Returns:
            Processed record dictionary or None if filtered out
        """
        try:
            # Extract basic fields
            title = record.get("Title", "")
            description = record.get("Description", "")
            html_content = record.get("Text", "")
            tags = record.get("Tags", [])
            properties = record.get("Properties", [])

            # Clean HTML content
            cleaned_content = self.clean_html_content(html_content)

            # Extract dream symbol
            dream_symbol = self.extract_dream_symbol(title)

            # Clean tags
            cleaned_tags = self.clean_tags(tags)

            # Extract SEO content
            seo_content = self.extract_seo_content(properties)

            # Create processed record
            processed_record = {
                "original_id": record.get("_id", {}).get("$oid", ""),
                "title": title.strip(),
                "description": description.strip(),
                "cleaned_content": cleaned_content,
                "dream_symbol": dream_symbol,
                "tags": cleaned_tags,
                "seo_title": seo_content["seo_title"],
                "seo_description": seo_content["seo_description"],
                "original_length": len(html_content),
                "cleaned_length": len(cleaned_content),
                "publish_date": record.get("PublishDate", {}).get("$date", ""),
                "url": record.get("Url", ""),
            }

            # Validate quality
            if self.validate_record_quality(processed_record):
                self.processed_count += 1
                return processed_record
            else:
                self.filtered_count += 1
                logger.debug(f"Record filtered out: {title[:50]}...")
                return None

        except Exception as e:
            logger.error(f"Error processing record: {e}")
            self.filtered_count += 1
            return None

    def process_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of dream interpretation records.

        Args:
            records: List of raw MongoDB records

        Returns:
            List of processed and validated records
        """
        logger.info(f"Processing {len(records)} records...")

        processed_records = []
        self.processed_count = 0
        self.filtered_count = 0

        for i, record in enumerate(records):
            if i % 50 == 0:
                logger.info(f"Processing record {i+1}/{len(records)}")

            processed_record = self.process_single_record(record)
            if processed_record:
                processed_records.append(processed_record)

        logger.info(
            f"Processing complete: {self.processed_count} processed, "
            f"{self.filtered_count} filtered out"
        )

        return processed_records

    def get_processing_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed_count": self.processed_count,
            "filtered_count": self.filtered_count,
            "total_processed": self.processed_count + self.filtered_count,
        }
