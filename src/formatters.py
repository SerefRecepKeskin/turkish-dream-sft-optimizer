# SFT format dönüşüm modülü
# Turkish Dream SFT Optimizer - Formatters
"""
SFT formatting module for OpenAI and Cohere platforms.
Converts processed dream interpretation data to platform-specific training formats.
"""

import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BaseSFTFormatter(ABC):
    """Base class for SFT formatters."""

    def __init__(self):
        self.formatted_count = 0

        # Turkish dream interpretation question templates
        self.question_templates = [
            "Rüyamda {symbol} gördüm, ne anlama gelir?",
            "Rüyada {symbol} görmek neye işaret eder?",
            "{symbol} rüyası nasıl yorumlanır?",
            "Rüyada {symbol} görmenin anlamı nedir?",
            "{symbol} rüyasının tabiri nedir?",
            "Rüyamda {symbol} vardı, bu neyi ifade eder?",
            "Rüyada {symbol} görmek iyi mi kötü mü?",
            "{symbol} ile ilgili rüyamın açıklaması nedir?",
            "Rüyada {symbol} görmek hakkında ne dersiniz?",
            "{symbol} rüyasının İslami yorumu nedir?",
        ]

        # System message for Turkish dream interpretation
        self.system_message = """Sen uzman bir Türk rüya yorumcususun. Türk kültürü ve İslami geleneklere uygun olarak rüya tabirlerini açıklarsın. Rüyaları yorumlarken:

1. Türk halk kültürü ve İslami kaynaklara dayanarak açıklama yap
2. Hem olumlu hem olumsuz anlamları belirt
3. Kültürel bağlamı ve geleneksel yorumları dahil et
4. Açıklayıcı ve anlayışlı bir dil kullan
5. Rüya sahibinin durumuna göre farklı yorumlar olabileceğini belirt"""

    @abstractmethod
    def format_single_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format a single record for the specific platform."""
        pass

    def generate_questions(
        self, dream_symbol: str, record: Dict[str, Any]
    ) -> List[str]:
        """
        Generate diverse questions for the dream symbol.

        Args:
            dream_symbol: Main dream symbol
            record: Processed record

        Returns:
            List of diverse questions
        """
        questions = []

        # Use the main dream symbol
        if dream_symbol:
            # Basic symbol questions
            symbol_questions = [
                template.format(symbol=dream_symbol)
                for template in self.question_templates[:6]
            ]
            questions.extend(symbol_questions)

            # Add title-based question if different
            title = record.get("title", "")
            if title and dream_symbol.lower() not in title.lower():
                questions.append(f"{title} hakkında ne söyleyebilirsiniz?")

        # Fallback to title-based questions
        else:
            title = record.get("title", "")
            if title:
                questions.extend(
                    [
                        f"{title} ne anlama gelir?",
                        f"{title} nasıl yorumlanır?",
                        f"{title} hakkında bilgi verir misiniz?",
                    ]
                )

        # Add tag-based questions if available
        tags = record.get("tags", [])
        for tag in tags[:2]:  # Limit to 2 tags to avoid spam
            if tag and tag != dream_symbol:
                questions.append(f"Rüyada {tag} görmek neyi ifade eder?")

        return questions[:4]  # Limit to 4 questions per record for efficiency

    def clean_content_for_answer(self, content: str) -> str:
        """
        Clean and optimize content for training answers.

        Args:
            content: Raw cleaned content

        Returns:
            Optimized answer content
        """
        if not content:
            return ""

        # Split into paragraphs and clean
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

        # Filter out very short paragraphs (likely noise)
        paragraphs = [p for p in paragraphs if len(p) > 30]

        # Limit to reasonable length for training (first 3-4 paragraphs)
        if len(paragraphs) > 4:
            paragraphs = paragraphs[:4]

        # Join with proper spacing
        cleaned_content = "\n\n".join(paragraphs)

        # Final cleanup
        cleaned_content = cleaned_content.replace("  ", " ")
        cleaned_content = cleaned_content.strip()

        return cleaned_content

    def format_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format a batch of records for training.

        Args:
            records: List of processed records

        Returns:
            List of formatted training examples
        """
        logger.info(f"Formatting {len(records)} records for {self.__class__.__name__}")

        formatted_records = []
        self.formatted_count = 0

        for i, record in enumerate(records):
            if i % 50 == 0:
                logger.info(f"Formatting record {i+1}/{len(records)}")

            try:
                formatted_examples = self.format_single_record(record)
                formatted_records.extend(formatted_examples)
                self.formatted_count += len(formatted_examples)

            except Exception as e:
                logger.error(f"Error formatting record {i}: {e}")

        logger.info(
            f"Formatting complete: {self.formatted_count} training examples created"
        )
        return formatted_records


class OpenAIFormatter(BaseSFTFormatter):
    """Formatter for OpenAI fine-tuning format."""

    def format_single_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format a single record for OpenAI fine-tuning.

        Args:
            record: Processed dream interpretation record

        Returns:
            List of OpenAI format training examples
        """
        dream_symbol = record.get("dream_symbol", "")
        content = self.clean_content_for_answer(record.get("cleaned_content", ""))

        if not content:
            return []

        # Generate diverse questions
        questions = self.generate_questions(dream_symbol, record)

        formatted_examples = []
        for question in questions:
            example = {
                "messages": [
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": content},
                ],
                "metadata": {
                    "dream_symbol": dream_symbol,
                    "original_id": record.get("original_id", ""),
                    "source_url": record.get("url", ""),
                },
            }
            formatted_examples.append(example)

        return formatted_examples


class CohereFormatter(BaseSFTFormatter):
    """Formatter for Cohere fine-tuning format."""

    def format_single_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format a single record for Cohere fine-tuning.

        Args:
            record: Processed dream interpretation record

        Returns:
            List of Cohere format training examples
        """
        dream_symbol = record.get("dream_symbol", "")
        content = self.clean_content_for_answer(record.get("cleaned_content", ""))

        if not content:
            return []

        # Generate diverse questions
        questions = self.generate_questions(dream_symbol, record)

        formatted_examples = []
        for question in questions:
            # Add system context to the prompt for Cohere
            prompt_with_context = f"""Sen uzman bir Türk rüya yorumcususun. Türk kültürü ve İslami geleneklere uygun rüya tabirleri yaparsın.

Soru: {question}

Cevap:"""

            example = {
                "prompt": prompt_with_context,
                "completion": content,
                "metadata": {
                    "dream_symbol": dream_symbol,
                    "original_id": record.get("original_id", ""),
                    "source_url": record.get("url", ""),
                },
            }
            formatted_examples.append(example)

        return formatted_examples


class DataAugmenter:
    """Additional data augmentation utilities."""

    @staticmethod
    def create_negative_examples(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create negative examples for better training.

        Args:
            records: Processed records

        Returns:
            List of negative training examples
        """
        negative_examples = []

        # Common wrong interpretations to avoid
        wrong_interpretations = [
            "Bu rüyanın kesin bir anlamı yoktur.",
            "Rüyalar sadece hayal ürünüdür.",
            "Bunu yorumlamak mümkün değil.",
            "Bu konuda bir şey söyleyemem.",
        ]

        for record in records[:10]:  # Limit negative examples
            dream_symbol = record.get("dream_symbol", "")
            if dream_symbol:
                for wrong_answer in wrong_interpretations:
                    negative_example = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sen uzman bir Türk rüya yorumcususun.",
                            },
                            {
                                "role": "user",
                                "content": f"Rüyada {dream_symbol} görmek ne anlama gelir?",
                            },
                            {"role": "assistant", "content": wrong_answer},
                        ],
                        "weight": -1,  # Negative example weight
                    }
                    negative_examples.append(negative_example)

        return negative_examples
