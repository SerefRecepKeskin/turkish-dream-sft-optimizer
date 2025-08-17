"""
Quality checking and metrics module for dream interpretation dataset.
Analyzes data quality and provides improvement metrics.
"""

import logging
import re
from collections import Counter
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class QualityChecker:
    """Analyze and validate data quality for SFT training."""

    def __init__(self):
        self.turkish_dream_keywords = [
            "rüya",
            "rüyada",
            "görmek",
            "tabir",
            "yorumlanır",
            "delalet",
            "işaret",
            "anlam",
            "düşman",
            "hayır",
            "şer",
            "bereket",
            "rızk",
            "manevi",
            "maddi",
            "hane",
            "zarar",
            "fayda",
            "hayırlı",
        ]

        self.quality_issues = [
            "netcore",
            "seo",
            "amp",
            "milliyet",
            "pembenar",
            "çok fazla tekrar",
            "anlamsız",
            "test",
        ]

    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze the quality of dream interpretation content.

        Args:
            content: Cleaned content to analyze

        Returns:
            Dictionary with quality metrics
        """
        if not content:
            return {
                "quality_score": 0,
                "issues": ["empty_content"],
                "cultural_indicators": 0,
                "readability_score": 0,
            }

        issues = []
        quality_score = 100  # Start with perfect score

        # Check length
        if len(content) < 100:
            issues.append("too_short")
            quality_score -= 30
        elif len(content) > 5000:
            issues.append("too_long")
            quality_score -= 10

        # Check for Turkish dream interpretation indicators
        cultural_indicators = sum(
            1 for keyword in self.turkish_dream_keywords if keyword in content.lower()
        )

        if cultural_indicators < 3:
            issues.append("low_cultural_context")
            quality_score -= 20

        # Check for quality issues
        content_lower = content.lower()
        for issue in self.quality_issues:
            if issue in content_lower:
                issues.append(f"contains_{issue}")
                quality_score -= 15

        # Check readability (sentence structure)
        sentences = content.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(
            len(sentences), 1
        )

        readability_score = 100
        if avg_sentence_length > 30:
            readability_score -= 20
            issues.append("long_sentences")
        elif avg_sentence_length < 5:
            readability_score -= 10
            issues.append("short_sentences")

        # Check for repetitive content
        words = content.lower().split()
        word_freq = Counter(words)
        most_common = word_freq.most_common(10)

        if (
            most_common and most_common[0][1] > len(words) * 0.1
        ):  # Single word > 10% of content
            issues.append("repetitive_content")
            quality_score -= 15

        # Ensure minimum quality
        quality_score = max(0, quality_score)

        return {
            "quality_score": quality_score,
            "issues": issues,
            "cultural_indicators": cultural_indicators,
            "readability_score": readability_score,
            "content_length": len(content),
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_length,
            "unique_words": len(set(words)),
        }

    def analyze_dream_symbol_coverage(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze dream symbol coverage and diversity.

        Args:
            records: List of processed records

        Returns:
            Dictionary with symbol coverage metrics
        """
        symbols = [
            record.get("dream_symbol", "")
            for record in records
            if record.get("dream_symbol")
        ]
        symbol_counts = Counter(symbols)

        # Calculate diversity metrics
        total_symbols = len(symbols)
        unique_symbols = len(symbol_counts)

        # Find most and least common symbols
        most_common_symbols = symbol_counts.most_common(10)
        least_common_symbols = [
            (symbol, count) for symbol, count in symbol_counts.items() if count == 1
        ]

        # Calculate meaningful balance metrics
        if symbol_counts:
            # Distribution balance: How balanced is the distribution? (0-100, higher = better)
            most_common_count = symbol_counts.most_common(1)[0][1]
            dominance_ratio = most_common_count / total_symbols * 100
            distribution_balance = max(0, 100 - dominance_ratio)

            # Coverage quality: What % of symbols have good representation (5+ instances)?
            well_represented = sum(1 for count in symbol_counts.values() if count >= 5)
            coverage_quality = (
                (well_represented / unique_symbols * 100) if unique_symbols > 0 else 0
            )
        else:
            distribution_balance = 0
            coverage_quality = 0

        return {
            "total_symbol_instances": total_symbols,
            "unique_symbols": unique_symbols,
            "distribution_balance_score": round(distribution_balance, 2),
            "coverage_quality_score": round(coverage_quality, 2),
            "most_common_symbols": most_common_symbols,
            "singleton_symbols": len(least_common_symbols),
            "avg_instances_per_symbol": round(
                total_symbols / max(unique_symbols, 1), 2
            ),
        }

    def analyze_content_completeness(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze completeness of essential fields.

        Args:
            records: List of processed records

        Returns:
            Dictionary with completeness metrics
        """
        total_records = len(records)

        completeness_metrics = {
            "has_title": sum(1 for r in records if r.get("title")),
            "has_content": sum(1 for r in records if r.get("cleaned_content")),
            "has_dream_symbol": sum(1 for r in records if r.get("dream_symbol")),
            "has_tags": sum(1 for r in records if r.get("tags")),
            "has_description": sum(1 for r in records if r.get("description")),
            "has_seo_title": sum(1 for r in records if r.get("seo_title")),
            "has_url": sum(1 for r in records if r.get("url")),
        }

        # Calculate percentages
        completeness_percentages = {
            field: (count / total_records * 100) if total_records > 0 else 0
            for field, count in completeness_metrics.items()
        }

        # Overall completeness score
        essential_fields = ["has_title", "has_content", "has_dream_symbol"]
        overall_completeness = sum(
            completeness_percentages[field] for field in essential_fields
        ) / len(essential_fields)

        return {
            "total_records": total_records,
            "completeness_counts": completeness_metrics,
            "completeness_percentages": completeness_percentages,
            "overall_completeness": overall_completeness,
        }

    def analyze_training_readiness(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze how ready the data is for SFT training.

        Args:
            records: List of processed records

        Returns:
            Dictionary with training readiness metrics
        """
        if not records:
            return {
                "training_ready_count": 0,
                "training_readiness_percentage": 0,
                "average_quality_score": 0,
                "recommendations": ["No records to analyze"],
            }

        # Analyze each record
        quality_scores = []
        training_ready = 0

        for record in records:
            content = record.get("cleaned_content", "")
            quality_analysis = self.analyze_content_quality(content)
            quality_scores.append(quality_analysis["quality_score"])

            # Consider training ready if quality score > 70 and has essential fields
            if (
                quality_analysis["quality_score"] > 70
                and record.get("dream_symbol")
                and len(content) >= 100
            ):
                training_ready += 1

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        readiness_percentage = (training_ready / len(records)) * 100

        # Generate recommendations
        recommendations = []
        if avg_quality < 70:
            recommendations.append("Improve content quality by better HTML cleaning")
        if readiness_percentage < 80:
            recommendations.append("Filter out low-quality records before training")
        if len(records) < 1000:
            recommendations.append(
                "Consider data augmentation to increase dataset size"
            )

        return {
            "training_ready_count": training_ready,
            "training_readiness_percentage": readiness_percentage,
            "average_quality_score": avg_quality,
            "quality_distribution": {
                "excellent": sum(1 for s in quality_scores if s >= 90),
                "good": sum(1 for s in quality_scores if 70 <= s < 90),
                "fair": sum(1 for s in quality_scores if 50 <= s < 70),
                "poor": sum(1 for s in quality_scores if s < 50),
            },
            "recommendations": recommendations,
        }

    def analyze_cultural_authenticity(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze cultural authenticity of Turkish dream interpretations.

        Args:
            records: List of processed records

        Returns:
            Dictionary with cultural authenticity metrics
        """
        # Keywords indicating Turkish/Islamic dream interpretation tradition
        traditional_indicators = [
            "alim",
            "tabir",
            "delalet",
            "işaret",
            "imam",
            "diyanet",
            "islami",
            "geleneksel",
            "halk",
            "kültür",
            "türk",
        ]

        islamic_keywords = [
            "allah",
            "peygamber",
            "dua",
            "namaz",
            "haram",
            "helal",
            "sevap",
            "günah",
            "ahiret",
            "cennet",
            "cehennem",
        ]

        cultural_scores = []
        has_traditional_context = 0
        has_islamic_context = 0

        for record in records:
            content = record.get("cleaned_content", "").lower()

            # Count traditional indicators
            traditional_count = sum(
                1 for indicator in traditional_indicators if indicator in content
            )
            islamic_count = sum(1 for keyword in islamic_keywords if keyword in content)

            cultural_score = min(100, (traditional_count * 10) + (islamic_count * 5))
            cultural_scores.append(cultural_score)

            if traditional_count > 0:
                has_traditional_context += 1
            if islamic_count > 0:
                has_islamic_context += 1

        avg_cultural_score = (
            sum(cultural_scores) / len(cultural_scores) if cultural_scores else 0
        )

        return {
            "average_cultural_authenticity": avg_cultural_score,
            "records_with_traditional_context": has_traditional_context,
            "records_with_islamic_context": has_islamic_context,
            "traditional_context_percentage": (has_traditional_context / len(records))
            * 100,
            "islamic_context_percentage": (has_islamic_context / len(records)) * 100,
            "cultural_authenticity_distribution": {
                "high": sum(1 for s in cultural_scores if s >= 50),
                "medium": sum(1 for s in cultural_scores if 20 <= s < 50),
                "low": sum(1 for s in cultural_scores if s < 20),
            },
        }

    def analyze_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive quality analysis on a batch of records.

        Args:
            records: List of processed records

        Returns:
            Comprehensive quality report
        """
        logger.info(f"Analyzing quality for {len(records)} records...")

        # Run all analyses
        symbol_coverage = self.analyze_dream_symbol_coverage(records)
        completeness = self.analyze_content_completeness(records)
        training_readiness = self.analyze_training_readiness(records)
        cultural_authenticity = self.analyze_cultural_authenticity(records)

        # Calculate overall quality score
        overall_scores = [
            completeness["overall_completeness"],
            training_readiness["training_readiness_percentage"],
            cultural_authenticity["average_cultural_authenticity"],
            symbol_coverage["distribution_balance_score"],
        ]

        overall_quality_score = sum(overall_scores) / len(overall_scores)

        # Determine quality grade
        if overall_quality_score >= 90:
            quality_grade = "EXCELLENT"
        elif overall_quality_score >= 75:
            quality_grade = "GOOD"
        elif overall_quality_score >= 60:
            quality_grade = "FAIR"
        else:
            quality_grade = "NEEDS_IMPROVEMENT"

        return {
            "quality_summary": {
                "overall_quality_score": round(overall_quality_score, 2),
                "quality_grade": quality_grade,
                "total_records_analyzed": len(records),
            },
            "symbol_coverage_analysis": symbol_coverage,
            "content_completeness_analysis": completeness,
            "training_readiness_analysis": training_readiness,
            "cultural_authenticity_analysis": cultural_authenticity,
            "improvement_recommendations": self._generate_improvement_recommendations(
                overall_quality_score, training_readiness, cultural_authenticity
            ),
        }

    def _generate_improvement_recommendations(
        self,
        overall_score: float,
        training_readiness: Dict[str, Any],
        cultural_authenticity: Dict[str, Any],
    ) -> List[str]:
        """Generate specific improvement recommendations."""
        recommendations = []

        if overall_score < 70:
            recommendations.append("Overall data quality needs significant improvement")

        if training_readiness["training_readiness_percentage"] < 80:
            recommendations.append("Consider additional data cleaning and filtering")

        if cultural_authenticity["average_cultural_authenticity"] < 30:
            recommendations.append(
                "Enhance cultural context preservation in content cleaning"
            )

        if training_readiness["average_quality_score"] < 70:
            recommendations.append(
                "Improve HTML cleaning and content extraction algorithms"
            )

        # Add positive recommendations for high-quality data
        if overall_score >= 80:
            recommendations.append("Data quality is excellent - ready for SFT training")

        if training_readiness["training_readiness_percentage"] >= 90:
            recommendations.append(
                "High training readiness - consider advanced data augmentation"
            )

        return recommendations
