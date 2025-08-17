"""
Cohere formatter for Turkish Dream SFT Optimizer.
Converts processed dream data to Cohere fine-tuning format.
"""

from typing import Any, Dict, List

from .base import BaseSFTFormatter


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
