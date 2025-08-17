"""
Parallel processing module for high-performance dream data processing.
Implements multi-threading with dynamic core allocation and chunk-based processing.
"""

import logging
import multiprocessing as mp
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

from ..formatters import CohereFormatter, OpenAIFormatter
from .data_processor import DreamDataProcessor
from .quality_checker import QualityChecker

logger = logging.getLogger(__name__)


class ParallelDreamProcessor:
    """High-performance parallel processor for dream interpretation data."""

    def __init__(
        self, max_workers: Optional[int] = None, chunk_size: Optional[int] = None
    ):
        """
        Initialize parallel processor.

        Args:
            max_workers: Maximum number of threads (default: from env config or CPU cores)
            chunk_size: Records per chunk (default: from env config or auto-calculated)
        """
        # Import here to avoid circular imports
        try:
            from ..utils.env_config import env_config

            default_max_workers = env_config.max_workers
            default_chunk_size = env_config.chunk_size
        except ImportError:
            default_max_workers = None
            default_chunk_size = None

        self.cpu_count = mp.cpu_count()
        self.max_workers = (
            max_workers or default_max_workers or min(self.cpu_count, 8)
        )  # Cap at 8 for efficiency
        self.chunk_size = chunk_size or default_chunk_size

        # Thread-safe counters
        self._lock = Lock()
        self._processed_count = 0
        self._total_records = 0

        logger.info(
            f"🚀 Parallel processor initialized: {self.max_workers} workers, "
            f"{self.cpu_count} CPU cores detected"
        )

    def calculate_optimal_chunk_size(self, total_records: int) -> int:
        """
        Calculate optimal chunk size based on data size and CPU cores.

        Args:
            total_records: Total number of records to process

        Returns:
            Optimal chunk size for parallel processing
        """
        if self.chunk_size:
            return self.chunk_size

        # Dynamic chunk sizing based on data size
        if total_records <= 100:
            return max(1, total_records // self.max_workers)
        elif total_records <= 500:
            return max(10, total_records // (self.max_workers * 2))
        elif total_records <= 2000:
            return max(25, total_records // (self.max_workers * 3))
        else:
            return max(50, total_records // (self.max_workers * 4))

    def create_chunks(
        self, records: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Split records into optimal chunks for parallel processing.

        Args:
            records: List of records to chunk

        Returns:
            List of record chunks
        """
        chunk_size = self.calculate_optimal_chunk_size(len(records))
        chunks = []

        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]
            chunks.append(chunk)

        logger.info(f"📦 Created {len(chunks)} chunks of ~{chunk_size} records each")
        return chunks

    def process_chunk(
        self, chunk_data: Tuple[int, List[Dict[str, Any]], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a single chunk of records.

        Args:
            chunk_data: Tuple of (chunk_id, records, config)

        Returns:
            Processing results for the chunk
        """
        chunk_id, records, config = chunk_data
        start_time = time.time()

        try:
            # Initialize processors for this thread
            processor = DreamDataProcessor(
                min_content_length=config.get("min_content_length", 100)
            )
            openai_formatter = OpenAIFormatter()
            cohere_formatter = CohereFormatter()

            # Process records
            processed_records = processor.process_batch(records)

            # Format for SFT
            openai_records = openai_formatter.format_batch(processed_records)
            cohere_records = cohere_formatter.format_batch(processed_records)

            # Update global counters (thread-safe)
            with self._lock:
                self._processed_count += len(processed_records)

            processing_time = time.time() - start_time

            logger.info(
                f"✅ Chunk {chunk_id}: {len(processed_records)} records "
                f"processed in {processing_time:.2f}s"
            )

            return {
                "chunk_id": chunk_id,
                "processed_records": processed_records,
                "openai_records": openai_records,
                "cohere_records": cohere_records,
                "processing_time": processing_time,
                "original_count": len(records),
                "processed_count": len(processed_records),
                "success": True,
            }

        except Exception as e:
            logger.error(f"❌ Chunk {chunk_id} failed: {e}")
            return {"chunk_id": chunk_id, "error": str(e), "success": False}

    def process_parallel(
        self, records: List[Dict[str, Any]], config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process records in parallel using multi-threading.

        Args:
            records: List of records to process
            config: Processing configuration

        Returns:
            Combined processing results
        """
        if not records:
            return {"processed_records": [], "openai_records": [], "cohere_records": []}

        config = config or {}
        self._total_records = len(records)
        self._processed_count = 0

        start_time = time.time()
        logger.info(
            f"🔄 Starting parallel processing: {len(records)} records, "
            f"{self.max_workers} workers"
        )

        # Create chunks
        chunks = self.create_chunks(records)
        chunk_data = [(i, chunk, config) for i, chunk in enumerate(chunks)]

        # Process chunks in parallel
        results = []
        failed_chunks = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(self.process_chunk, data): data[0]
                for data in chunk_data
            }

            # Collect results as they complete
            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]
                try:
                    result = future.result()
                    if result["success"]:
                        results.append(result)
                    else:
                        failed_chunks.append(chunk_id)

                except Exception as e:
                    logger.error(
                        f"❌ Future execution failed for chunk {chunk_id}: {e}"
                    )
                    failed_chunks.append(chunk_id)

        # Combine all results
        combined_results = self._combine_results(results)

        total_time = time.time() - start_time

        # Log performance metrics
        self._log_performance_metrics(
            total_records=len(records),
            processed_records=len(combined_results["processed_records"]),
            total_time=total_time,
            failed_chunks=failed_chunks,
        )

        combined_results["processing_time"] = total_time
        combined_results["failed_chunks"] = failed_chunks

        return combined_results

    def _combine_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from all chunks."""
        combined = {"processed_records": [], "openai_records": [], "cohere_records": []}

        # Sort results by chunk_id to maintain order
        results.sort(key=lambda x: x["chunk_id"])

        for result in results:
            combined["processed_records"].extend(result["processed_records"])
            combined["openai_records"].extend(result["openai_records"])
            combined["cohere_records"].extend(result["cohere_records"])

        return combined

    def _log_performance_metrics(
        self,
        total_records: int,
        processed_records: int,
        total_time: float,
        failed_chunks: List[int],
    ):
        """Log detailed performance metrics."""
        records_per_second = processed_records / total_time if total_time > 0 else 0
        speedup_estimate = self.max_workers * 0.7  # Realistic speedup with overhead

        logger.info("📊 PARALLEL PROCESSING COMPLETED")
        logger.info(f"⏱️  Total time: {total_time:.2f} seconds")
        logger.info(f"📈 Records/second: {records_per_second:.1f}")
        logger.info(f"🔄 Workers used: {self.max_workers}")
        logger.info(
            f"✅ Success rate: {processed_records}/{total_records} "
            f"({processed_records/total_records*100:.1f}%)"
        )

        if failed_chunks:
            logger.warning(f"⚠️  Failed chunks: {len(failed_chunks)} - {failed_chunks}")

        # Performance comparison
        estimated_sequential_time = total_time * speedup_estimate
        logger.info(
            f"🚀 Estimated speedup: {speedup_estimate:.1f}x "
            f"(sequential would take ~{estimated_sequential_time:.1f}s)"
        )


class PerformanceOptimizer:
    """Additional performance optimization utilities."""

    @staticmethod
    def estimate_optimal_workers(
        record_count: int, avg_record_size_kb: float = 10
    ) -> int:
        """
        Estimate optimal number of workers based on data characteristics.

        Args:
            record_count: Number of records to process
            avg_record_size_kb: Average record size in KB

        Returns:
            Optimal number of workers
        """
        cpu_count = mp.cpu_count()

        # Memory-based calculation
        total_data_mb = (record_count * avg_record_size_kb) / 1024

        if total_data_mb < 50:  # Small dataset
            return min(cpu_count, 4)
        elif total_data_mb < 200:  # Medium dataset
            return min(cpu_count, 6)
        else:  # Large dataset
            return min(cpu_count, 8)

    @staticmethod
    def benchmark_processing_speed(
        sample_records: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Benchmark processing speed to optimize chunk size.

        Args:
            sample_records: Small sample for benchmarking

        Returns:
            Benchmark results
        """
        if len(sample_records) < 10:
            return {"records_per_second": 0, "avg_processing_time": 0}

        # Test with small sample
        start_time = time.time()
        processor = DreamDataProcessor()

        sample_size = min(10, len(sample_records))
        processed = processor.process_batch(sample_records[:sample_size])

        processing_time = time.time() - start_time
        records_per_second = sample_size / processing_time if processing_time > 0 else 0

        return {
            "records_per_second": records_per_second,
            "avg_processing_time": processing_time / sample_size,
            "sample_size": sample_size,
        }


# Factory function for easy integration
def create_parallel_processor(
    record_count: int, max_workers: int = None, auto_optimize: bool = True
) -> ParallelDreamProcessor:
    """
    Factory function to create optimized parallel processor.

    Args:
        record_count: Number of records to process
        max_workers: Manual worker count (None for auto)
        auto_optimize: Whether to auto-optimize settings

    Returns:
        Configured ParallelDreamProcessor
    """
    if auto_optimize and not max_workers:
        max_workers = PerformanceOptimizer.estimate_optimal_workers(record_count)

    return ParallelDreamProcessor(max_workers=max_workers)
