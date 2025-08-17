# Usage Examples

## Basic Processing

### Simple Dataset Processing

```python
from src.core import DreamDataProcessor
from src.formatters import OpenAIFormatter, CohereFormatter
from src.utils import FileHandler

# Load data
data = FileHandler.load_json("dreams_500.json")

# Process data
processor = DreamDataProcessor(min_content_length=100)
processed_data = processor.process_batch(data)

# Format for OpenAI
openai_formatter = OpenAIFormatter()
openai_records = openai_formatter.format_batch(processed_data)

# Format for Cohere
cohere_formatter = CohereFormatter()
cohere_records = cohere_formatter.format_batch(processed_data)

# Save results
FileHandler.save_jsonl(openai_records, "output/openai_format.jsonl")
FileHandler.save_jsonl(cohere_records, "output/cohere_format.jsonl")
```

### Command Line Usage

```bash
# Basic processing
python3 main.py --input dreams_500.json --output-dir output/

# With parallel processing (recommended for large datasets)
python3 main.py --input dreams_500.json --output-dir output/ --parallel

# With custom parameters and benchmarking
python3 main.py \
  --input dreams_500.json \
  --output-dir output/ \
  --min-content-length 150 \
  --parallel \
  --max-workers 8 \
  --benchmark
```

### Environment Configuration (.env)

```bash
# Create .env file for consistent configuration
cat > .env << EOF
# Data Processing
MIN_CONTENT_LENGTH=100
OUTPUT_DIR=output/

# Parallel Processing
MAX_WORKERS=8
CHUNK_SIZE=50

# Quality Control
MIN_QUALITY_SCORE=70
ENABLE_STRICT_VALIDATION=true
MAX_VALIDATION_ERRORS=10

# Output Control
SAVE_OPENAI_FORMAT=true
SAVE_COHERE_FORMAT=true
SAVE_PROCESSED_DATA=true
SAVE_QUALITY_REPORT=true

# Performance
ENABLE_BENCHMARKING=false
LOG_LEVEL=INFO
EOF

# Now run with environment configuration
python3 main.py --input dreams_500.json
```

## Advanced Processing

### Parallel Processing with Optimization

```python
from src.core import create_parallel_processor
from src.utils import FileHandler

# Load data
data = FileHandler.load_json("dreams_500.json")

# Create optimized parallel processor
processor = create_parallel_processor(
    record_count=len(data),
    max_workers=None,  # Auto-detect optimal workers
    auto_optimize=True
)

# Process with custom configuration
config = {
    "min_content_length": 150,
    "max_content_length": 3000,
    "preserve_cultural_context": True
}

results = processor.process_parallel(data, config)

# Results contain all formatted outputs
processed_records = results["processed_records"]
openai_records = results["openai_records"]
cohere_records = results["cohere_records"]

# Save all outputs
FileHandler.save_json(processed_records, "output/processed_data.json")
FileHandler.save_jsonl(openai_records, "output/openai_format.jsonl")
FileHandler.save_jsonl(cohere_records, "output/cohere_format.jsonl")

# View processing statistics
print(f"Processing time: {results['processing_stats']['total_time']:.2f}s")
print(f"Records per second: {results['processing_stats']['records_per_second']:.1f}")
```

### Quality Analysis and Filtering

```python
from src.core import QualityChecker
from src.utils import DataValidator

# Comprehensive quality analysis
checker = QualityChecker()
quality_metrics = checker.analyze_batch(processed_data)

print(f"Overall quality score: {quality_metrics['overall_quality_score']:.2f}")
print(f"Training readiness: {quality_metrics['training_readiness']}")
print(f"Cultural context score: {quality_metrics['cultural_context_average']:.2f}")

# Filter high-quality records
high_quality_records = []
for record in processed_data:
    content_score = checker.calculate_content_quality(record.get("cleaned_content", ""))
    if content_score >= 80:  # Only keep high-quality records
        high_quality_records.append(record)

print(f"High quality records: {len(high_quality_records)}/{len(processed_data)}")

# Validate output formats
openai_valid = DataValidator.validate_sft_records(openai_records, "openai")
cohere_valid = DataValidator.validate_sft_records(cohere_records, "cohere")
print(f"OpenAI format valid: {openai_valid}")
print(f"Cohere format valid: {cohere_valid}")
```

## Performance Monitoring

### Benchmarking and Optimization

```python
from src.core import PerformanceOptimizer
import time

def benchmark_processing_methods(data: list):
    """Compare sequential vs parallel processing performance."""
    
    # Test sequential processing
    start_time = time.time()
    processor = DreamDataProcessor()
    sequential_results = processor.process_batch(data[:100])  # Test subset
    sequential_time = time.time() - start_time
    
    # Test parallel processing
    start_time = time.time()
    parallel_processor = create_parallel_processor(
        record_count=100,
        auto_optimize=True
    )
    parallel_results = parallel_processor.process_parallel(data[:100], {})
    parallel_time = time.time() - start_time
    
    # Compare results
    print(f"Sequential processing: {sequential_time:.2f}s")
    print(f"Parallel processing: {parallel_time:.2f}s")
    print(f"Speedup: {sequential_time/parallel_time:.2f}x")
    
    return {
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "speedup": sequential_time / parallel_time
    }

# Run benchmark
benchmark_results = benchmark_processing_methods(data)

# Get system optimization recommendations
system_stats = PerformanceOptimizer.get_system_info()
print(f"Recommended workers: {system_stats['recommended_workers']}")
print(f"Available memory: {system_stats['available_memory_gb']:.1f} GB")
```

## Custom Development

### Creating a Custom Formatter

```python
from src.formatters.base import BaseSFTFormatter
from typing import Dict, List, Any

class CustomPlatformFormatter(BaseSFTFormatter):
    """Custom SFT formatter for specific platform requirements."""
    
    def __init__(self, custom_template: str = None):
        super().__init__()
        self.custom_template = custom_template or "Custom: {symbol} - {content}"
    
    def format_single_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format single record for custom platform."""
        dream_symbol = record.get("dream_symbol", "")
        content = self.clean_content_for_answer(record.get("cleaned_content", ""))
        
        if not content or len(content) < 50:
            return []
        
        # Generate custom format
        formatted_record = {
            "id": record.get("original_id", ""),
            "symbol": dream_symbol,
            "interpretation": content,
            "cultural_context": "Turkish dream interpretation",
            "quality_score": self._calculate_quality_score(record),
            "training_data": {
                "input": f"What does {dream_symbol} mean in dreams?",
                "output": content,
                "metadata": {
                    "language": "Turkish",
                    "domain": "dream_interpretation"
                }
            }
        }
        
        return [formatted_record]
    
    def _calculate_quality_score(self, record: Dict[str, Any]) -> float:
        """Calculate quality score for record."""
        score = 0.0
        content = record.get("cleaned_content", "")
        
        if len(content) > 100: score += 0.3
        if record.get("dream_symbol"): score += 0.3
        if record.get("tags"): score += 0.2
        if "rüya" in content.lower(): score += 0.2
        
        return min(score, 1.0)

# Usage
custom_formatter = CustomPlatformFormatter()
custom_records = custom_formatter.format_batch(processed_data)
FileHandler.save_json(custom_records, "output/custom_format.json")
```

## Integration Examples

### Simple API Server

```python
from flask import Flask, request, jsonify
from src.core import DreamDataProcessor, create_parallel_processor
from src.formatters import OpenAIFormatter, CohereFormatter
from src.utils import setup_logger

app = Flask(__name__)
logger = setup_logger(__name__)

@app.route('/process', methods=['POST'])
def process_dreams():
    """API endpoint for processing dream data."""
    try:
        data = request.json.get('records', [])
        format_type = request.json.get('format', 'openai')  # 'openai' or 'cohere'
        parallel = request.json.get('parallel', False)
        
        if not data:
            return jsonify({'error': 'No records provided'}), 400
        
        # Choose processing method
        if parallel and len(data) > 10:
            processor = create_parallel_processor(
                record_count=len(data),
                auto_optimize=True
            )
            results = processor.process_parallel(data, {})
            processed_data = results["processed_records"]
            
            if format_type == 'openai':
                formatted_data = results["openai_records"]
            else:
                formatted_data = results["cohere_records"]
        else:
            # Sequential processing
            processor = DreamDataProcessor()
            processed_data = processor.process_batch(data)
            
            if format_type == 'openai':
                formatter = OpenAIFormatter()
            else:
                formatter = CohereFormatter()
            
            formatted_data = formatter.format_batch(processed_data)
        
        return jsonify({
            'success': True,
            'processed_count': len(processed_data),
            'formatted_count': len(formatted_data),
            'format': format_type,
            'data': formatted_data[:10],  # Return first 10 for preview
            'total_available': len(formatted_data)
        })
    
    except Exception as e:
        logger.error(f"API processing error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'turkish-dream-optimizer'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Data Analysis and Validation

### Comprehensive Data Analysis

```python
import pandas as pd
from src.core import QualityChecker
from src.utils import DataValidator

def analyze_processing_results(processed_data: list, openai_data: list, cohere_data: list):
    """Comprehensive analysis of processing results."""
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(processed_data)
    
    # Basic statistics
    print("=== Processing Results Analysis ===")
    print(f"Total records processed: {len(df)}")
    print(f"Average content length: {df['cleaned_content'].str.len().mean():.1f} characters")
    print(f"Content length std: {df['cleaned_content'].str.len().std():.1f}")
    
    # Symbol analysis
    if 'dream_symbol' in df.columns:
        unique_symbols = df['dream_symbol'].nunique()
        print(f"Unique dream symbols: {unique_symbols}")
        
        # Top symbols
        top_symbols = df['dream_symbol'].value_counts().head(10)
        print("\nTop 10 Dream Symbols:")
        for symbol, count in top_symbols.items():
            print(f"  {symbol}: {count}")
    
    # Quality analysis
    checker = QualityChecker()
    quality_metrics = checker.analyze_batch(processed_data)
    
    print(f"\n=== Quality Metrics ===")
    print(f"Overall quality score: {quality_metrics.get('overall_quality_score', 0):.2f}")
    print(f"Training readiness: {quality_metrics.get('training_readiness', 'Unknown')}")
    
    # Format validation
    openai_valid = DataValidator.validate_sft_records(openai_data, "openai")
    cohere_valid = DataValidator.validate_sft_records(cohere_data, "cohere")
    
    print(f"\n=== Format Validation ===")
    print(f"OpenAI format valid: {openai_valid}")
    print(f"Cohere format valid: {cohere_valid}")
    print(f"OpenAI records: {len(openai_data)}")
    print(f"Cohere records: {len(cohere_data)}")
    
    return {
        'basic_stats': {
            'total_records': len(df),
            'avg_content_length': df['cleaned_content'].str.len().mean(),
            'unique_symbols': unique_symbols if 'dream_symbol' in df.columns else 0
        },
        'quality_metrics': quality_metrics,
        'format_validation': {
            'openai_valid': openai_valid,
            'cohere_valid': cohere_valid
        }
    }

# Usage after processing
analysis_results = analyze_processing_results(processed_data, openai_records, cohere_records)
```
