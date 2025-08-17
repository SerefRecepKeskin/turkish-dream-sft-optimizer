# API Reference

## Core Modules (`src/core/`)

### DreamDataProcessor

Main class for processing and cleaning dream interpretation data.

```python
from src.core import DreamDataProcessor

processor = DreamDataProcessor(
    min_content_length=100  # Can be None to use env config
)
```

**Constructor Parameters:**
- `min_content_length` (Optional[int]): Minimum content length threshold. If None, uses `MIN_CONTENT_LENGTH` from `.env` file (default: 100)

**Environment Integration:**
The processor automatically loads configuration from `.env` file:
- `MIN_CONTENT_LENGTH`: Minimum content length for filtering
- `MAX_CONTENT_LENGTH`: Maximum content length allowed  
- `MIN_CULTURAL_INDICATORS`: Minimum cultural context indicators

**Methods:**

- `clean_html_content(html_content: str) -> str`: Clean HTML content using BeautifulSoup
- `extract_dream_symbol(record: dict) -> str`: Extract main dream symbol from record
- `process_single_record(record: dict) -> dict`: Process and clean single record
- `process_batch(records: list) -> list`: Process multiple records sequentially
- `validate_record(record: dict) -> bool`: Validate record meets quality criteria

**Example Usage:**
```python
# Using default env config values
processor = DreamDataProcessor()
cleaned_records = processor.process_batch(raw_data)

# Override specific value
processor = DreamDataProcessor(min_content_length=150)
cleaned_records = processor.process_batch(raw_data)
```

### ParallelDreamProcessor

Optimized parallel processing for large datasets.

```python
from src.core import ParallelDreamProcessor, create_parallel_processor

# Direct instantiation
processor = ParallelDreamProcessor(max_workers=8, chunk_size=50)

# Factory function (recommended)
processor = create_parallel_processor(
    record_count=500,
    max_workers=None,  # Auto-detect
    auto_optimize=True
)
```

**Constructor Parameters:**
- `max_workers` (Optional[int]): Maximum number of worker threads. If None, uses `MAX_WORKERS` from `.env` file
- `chunk_size` (Optional[int]): Size of chunks for parallel processing. If None, uses `CHUNK_SIZE` from `.env` file

**Environment Integration:**
Automatically loads from `.env` file:
- `MAX_WORKERS`: Maximum number of parallel workers (empty = auto-detect)
- `CHUNK_SIZE`: Processing chunk size (empty = auto-calculate)

**Methods:**

- `process_parallel(records: list, config: dict) -> dict`: Process records in parallel
- `calculate_optimal_chunk_size(total_records: int) -> int`: Calculate optimal chunk size
- `get_optimal_worker_count() -> int`: Get optimal number of workers for current system

**Return Format:**
```python
{
    "processed_records": [...],
    "openai_records": [...],
    "cohere_records": [...],
    "processing_stats": {...}
}
```

### QualityChecker

Comprehensive quality analysis and metrics generation.

```python
from src.core import QualityChecker

checker = QualityChecker()
```

**Environment Integration:**
Automatically loads configuration from `.env` file:
- `MIN_QUALITY_SCORE`: Minimum quality threshold (0.0-1.0)
- `ENABLE_STRICT_VALIDATION`: Enable strict validation mode
- `MAX_VALIDATION_ERRORS`: Maximum validation errors to report

**Methods:**

- `analyze_single_record(record: dict) -> dict`: Analyze single record quality
- `analyze_batch(records: list) -> dict`: Analyze batch quality metrics
- `calculate_content_quality(content: str) -> float`: Calculate content quality score (0-100)
- `assess_cultural_context(content: str) -> dict`: Assess Turkish cultural indicators
- `check_symbol_coverage(records: list) -> dict`: Analyze dream symbol distribution

**Quality Metrics:**
```python
{
    "content_quality_scores": [...],
    "cultural_context_scores": [...],
    "symbol_coverage": {...},
    "training_readiness": "EXCELLENT" | "GOOD" | "FAIR" | "POOR"
}
```

### PerformanceOptimizer

Performance monitoring and optimization utilities.

```python
from src.core import PerformanceOptimizer

# Benchmark processing speed
results = PerformanceOptimizer.benchmark_processing_speed(sample_data)

# Monitor memory usage
stats = PerformanceOptimizer.monitor_memory_usage()
```

**Methods:**

- `benchmark_processing_speed(sample_data: list) -> dict`: Benchmark processing performance
- `monitor_memory_usage() -> dict`: Monitor current memory usage
- `optimize_parameters(record_count: int) -> dict`: Get optimized parameters

## Formatters (`src/formatters/`)

### BaseSFTFormatter

Abstract base class for all SFT formatters.

```python
from src.formatters.base import BaseSFTFormatter

class CustomFormatter(BaseSFTFormatter):
    def format_single_record(self, record: dict) -> dict:
        # Custom implementation
        pass
```

**Abstract Methods:**
- `format_single_record(record: dict) -> dict`: Format single record
- `get_format_name() -> str`: Return formatter name

**Common Methods:**
- `format_batch(records: list) -> list`: Format multiple records
- `validate_output(formatted_record: dict) -> bool`: Validate formatted output

### OpenAIFormatter

OpenAI ChatGPT format implementation.

```python
from src.formatters import OpenAIFormatter

formatter = OpenAIFormatter(
    system_message_template="custom_template",
    question_templates=["template1", "template2"]
)
```

**Constructor Parameters:**
- `system_message_template` (str, optional): Custom system message template
- `question_templates` (list, optional): Custom question templates
- `max_questions_per_record` (int): Maximum questions per record (default: 3)

**Output Format:**
```python
{
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

### CohereFormatter

Cohere platform format implementation.

```python
from src.formatters import CohereFormatter

formatter = CohereFormatter(
    prompt_template="custom_prompt",
    include_context=True
)
```

**Constructor Parameters:**
- `prompt_template` (str, optional): Custom prompt template
- `include_context` (bool): Include cultural context (default: True)
- `max_prompt_length` (int): Maximum prompt length (default: 2000)

**Output Format:**
```python
{
    "prompt": "Sen uzman bir Türk rüya yorumcususun...

Soru: ...

Cevap:",
    "completion": "Rüyada ... görmek genellikle ..."
}
```

## Utilities (`src/utils/`)

### Environment Configuration

Centralized environment variable management.

```python
from src.utils import env_config, get_env_var

# Access pre-loaded configuration
min_length = env_config.min_content_length
output_dir = env_config.output_dir
log_level = env_config.log_level

# Get individual environment variables with type conversion
custom_setting = get_env_var("CUSTOM_SETTING", default="default_value", var_type=str)
timeout = get_env_var("TIMEOUT", default=30, var_type=int)
debug_mode = get_env_var("DEBUG_MODE", default=False, var_type=bool)
```

**Available Configuration Properties:**
```python
# Processing
env_config.min_content_length          # MIN_CONTENT_LENGTH
env_config.max_content_length          # MAX_CONTENT_LENGTH  
env_config.min_cultural_indicators     # MIN_CULTURAL_INDICATORS

# Parallel Processing
env_config.max_workers                 # MAX_WORKERS
env_config.chunk_size                  # CHUNK_SIZE

# Output
env_config.output_dir                  # OUTPUT_DIR
env_config.save_processed_data         # SAVE_PROCESSED_DATA
env_config.save_openai_format          # SAVE_OPENAI_FORMAT
env_config.save_cohere_format          # SAVE_COHERE_FORMAT
env_config.save_quality_report         # SAVE_QUALITY_REPORT

# Logging
env_config.log_level                   # LOG_LEVEL
env_config.log_file                    # LOG_FILE

# Quality
env_config.min_quality_score           # MIN_QUALITY_SCORE
env_config.enable_strict_validation    # ENABLE_STRICT_VALIDATION
env_config.max_validation_errors       # MAX_VALIDATION_ERRORS
```

### FileHandler

Centralized file operations with error handling.

```python
from src.utils import FileHandler

# Load JSON data with validation
data = FileHandler.load_json("input.json")

# Save JSON data with formatting
FileHandler.save_json(data, "output.json", indent=2)

# Save JSONL data efficiently
FileHandler.save_jsonl(records, "output.jsonl")

# Ensure directory exists
path = FileHandler.ensure_directory("output/results")
```

**Methods:**

- `load_json(file_path: str) -> Union[dict, list]`: Load JSON file
- `save_json(data: Union[dict, list], file_path: str, **kwargs)`: Save JSON file
- `load_jsonl(file_path: str) -> list`: Load JSONL file
- `save_jsonl(records: list, file_path: str)`: Save JSONL file
- `ensure_directory(directory_path: str) -> Path`: Create directory if not exists

### DataValidator

Comprehensive data validation and quality assessment.

```python
from src.utils import DataValidator

# Validate input data structure
is_valid = DataValidator.validate_input_data(data)

# Validate SFT records format
is_valid = DataValidator.validate_sft_records(records, "openai")

# Get comprehensive quality score
score = DataValidator.get_data_quality_score(records)

# Check cultural indicators
cultural_score = DataValidator.assess_cultural_indicators(content)
```

**Methods:**
- `validate_input_data(data: list) -> bool`: Validate input data structure
- `validate_sft_records(records: list, format_type: str) -> bool`: Validate SFT format
- `get_data_quality_score(records: list) -> float`: Calculate quality score (0-100)
- `assess_cultural_indicators(content: str) -> float`: Assess Turkish cultural context

### Logger Setup

Structured logging configuration with automatic environment integration.

```python
from src.utils import setup_logger

# Basic logger setup (uses LOG_LEVEL from .env)
logger = setup_logger("my_module")

# Logger with custom file output (uses LOG_FILE from .env if not specified)
logger = setup_logger("my_module", log_file="custom.log")

# Override log level temporarily
logger = setup_logger("my_module", level="DEBUG")
```

**Environment Integration:**
Automatically uses configuration from `.env` file:
- `LOG_LEVEL`: Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE`: Default log file name

**Parameters:**
- `name` (str): Logger name (usually `__name__`)
- `level` (Optional[int]): Log level override (if None, uses LOG_LEVEL from `.env`)
- `log_file` (Optional[str]): Log file path (if None, uses LOG_FILE from `.env`)
- `console_output` (bool): Whether to output to console (default: True)

**Usage Example:**
```python
logger = setup_logger(__name__)
logger.info("Processing started")
logger.error("Error occurred", exc_info=True)
```

## Configuration Management

### Environment Variables

All configuration is managed through `.env` file with automatic loading:

```properties
# .env file example
MIN_CONTENT_LENGTH=100
LOG_LEVEL=INFO
OUTPUT_DIR=output
SAVE_OPENAI_FORMAT=true
MAX_WORKERS=4
```

**Priority Order:**
1. Command line arguments (highest)
2. Environment variables (`.env` file)  
3. Default values (lowest)

### Type Conversion

Environment variables are automatically converted to appropriate types:

```python
from src.utils import get_env_var

# String (default)
name = get_env_var("APP_NAME", "default-name")

# Integer
port = get_env_var("PORT", 8080, int)

# Boolean (accepts: true/false, 1/0, yes/no, on/off)
debug = get_env_var("DEBUG", False, bool)

# Float
threshold = get_env_var("THRESHOLD", 0.5, float)

# Required variable (raises ValueError if missing)
api_key = get_env_var("API_KEY", required=True)
```

## Error Handling

All modules implement comprehensive error handling with specific exception types:

```python
from src.core.exceptions import (
    ProcessingError,
    ValidationError,
    FormatError
)

try:
    processor.process_batch(data)
except ProcessingError as e:
    logger.error(f"Processing failed: {e}")
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
```

## Type Hints

All modules include comprehensive type hints for better IDE support and code clarity:

```python
from typing import Dict, List, Optional, Union

def process_records(
    records: List[Dict[str, Any]], 
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    pass
```
