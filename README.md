# Turkish Dream SFT Optimizer

## 🎯 Overview

This project optimizes Turkish dream interpretation datasets for Supervised Fine-Tuning (SFT) on OpenAI and Cohere platforms. It transforms raw MongoDB exports into high-quality training data, featuring a modular architecture with parallel processing capabilities and comprehensive environment-based configuration.

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/SerefRecepKeskin/turkish-dream-sft-optimizer.git
cd turkish-dream-sft-optimizer

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional - has sensible defaults)
cp .env.example .env
nano .env  # Edit configuration as needed

# Run the optimizer (basic usage)
python3 main.py --input dreams_500.json --output-dir output/

# Run with parallel processing for better performance
python3 main.py --input dreams_500.json --output-dir output/ --parallel

# Run with benchmark and custom settings
python3 main.py --input dreams_500.json --output-dir output/ --parallel --benchmark
```

## 📊 Problem Analysis

### Initial Challenges
- **Raw MongoDB Data**: 8K+ records with extensive metadata noise
- **HTML Content**: Mixed with SEO tags and formatting artifacts  
- **Poor SFT Performance**: Initial attempts achieved only 52% accuracy
- **Cultural Context**: Need to preserve Turkish cultural and Islamic interpretations

### Solution Approach
1. **Modular Architecture**: Clean separation of concerns with specialized modules
2. **Parallel Processing**: Multi-threaded processing for performance optimization
3. **Intelligent Content Extraction**: Advanced HTML cleaning and content preservation
4. **Cultural Context Preservation**: Maintain Turkish dream interpretation traditions
5. **Multi-Format Output**: Generate both OpenAI and Cohere compatible formats
6. **Quality Enhancement**: Comprehensive filtering and validation system
7. **Environment Configuration**: Flexible `.env` based configuration management

## 🏗️ Architecture

```
turkish-dream-sft-optimizer/
├── main.py                    # Main execution script
├── src/                       # Source code modules
│   ├── core/                  # Core processing modules
│   │   ├── data_processor.py  # Data cleaning and processing
│   │   ├── parallel_processor.py # Parallel processing optimization
│   │   └── quality_checker.py # Quality analysis and metrics
│   ├── formatters/            # SFT format generators
│   │   ├── base.py           # Base formatter interface
│   │   ├── openai.py         # OpenAI format implementation
│   │   └── cohere.py         # Cohere format implementation
│   └── utils/                 # Utility modules
│       ├── file_handler.py   # File operations
│       ├── logger.py         # Logging configuration
│       ├── validators.py     # Data validation
│       └── env_config.py     # Environment configuration
├── .env                       # Environment configuration file
├── .env.example              # Environment configuration template
├── data/                      # Data directories
│   ├── raw/                  # Raw input data
│   ├── processed/            # Intermediate processed data
│   └── samples/              # Sample/test data
├── output/                    # Generated outputs
│   ├── openai_format.jsonl
│   ├── cohere_format.jsonl
│   ├── processed_data.json
│   └── quality_report.json
├── docs/                      # Documentation
│   ├── api_reference.md      # API documentation
│   ├── examples/             # Usage examples
│   └── performance_guide.md  # Performance optimization guide
└── requirements.txt           # Dependencies
```

## 🔧 Core Components

### Core Processing Modules (`src/core/`)

#### DataProcessor
- **HTML Cleaning**: BeautifulSoup-based content extraction
- **Symbol Extraction**: Intelligent dream symbol identification
- **Tag Filtering**: Remove SEO noise and enhance relevant tags
- **Quality Validation**: Multi-criteria content quality assessment

#### Parallel Processor
- **Performance Optimization**: Multi-threaded processing for large datasets
- **Dynamic Worker Management**: Automatic worker count optimization
- **Memory Efficiency**: Optimized memory usage for batch processing
- **Progress Tracking**: Real-time processing progress monitoring

#### Quality Checker
- **Content Analysis**: Cultural context and readability scoring
- **Symbol Coverage**: Dream symbol distribution analysis
- **Training Readiness**: Comprehensive quality metrics
- **Improvement Tracking**: Before/after comparison

### SFT Formatters (`src/formatters/`)

#### Base Formatter
- **Abstract Interface**: Common formatting interface for all platforms
- **Validation Logic**: Ensure format compliance and quality
- **Error Handling**: Robust error recovery and logging

#### OpenAI Formatter
- **Messages Format**: Conversation-based format for ChatGPT training
- **System Messages**: Cultural context for Turkish dream interpretation
- **Role Management**: Proper user/assistant role assignment

#### Cohere Formatter
- **Prompt-Completion**: Optimized for Cohere platform requirements
- **Template System**: Flexible prompt template generation
- **Context Preservation**: Maintain cultural and linguistic context

### Utility Modules (`src/utils/`)

#### File Handler
- **JSON/JSONL Operations**: Efficient file reading and writing
- **Directory Management**: Automatic directory creation and organization
- **Error Recovery**: Robust file operation error handling

#### Logger
- **Structured Logging**: Comprehensive logging with configurable levels from `.env`
- **Progress Tracking**: Real-time processing feedback
- **Error Reporting**: Detailed error tracking and reporting

#### Environment Configuration
- **Flexible Settings**: `.env` file based configuration system
- **Runtime Overrides**: Command line arguments override environment settings
- **Auto-loading**: Automatic detection and loading of `.env` files

#### Validators
- **Data Validation**: Input data integrity checks
- **Format Validation**: Output format compliance verification
- **Quality Metrics**: Content quality scoring and assessment

## 📋 Usage Examples

### Basic Usage
```bash
# Simple processing with default settings
python3 main.py --input dreams_500.json --output-dir output/

# With custom content length threshold
python3 main.py --input dreams_500.json --output-dir output/ --min-content-length 150
```

### Advanced Usage
```bash
# Parallel processing (recommended for large datasets)
python3 main.py --input dreams_500.json --output-dir output/ --parallel

# Parallel processing with custom worker count
python3 main.py --input dreams_500.json --output-dir output/ --parallel --max-workers 8

# With performance benchmark
python3 main.py --input dreams_500.json --output-dir output/ --benchmark --parallel
```

### Configuration Options
```bash
# Environment variables for custom configuration
export LOG_LEVEL=DEBUG
export MAX_CONTENT_LENGTH=5000
export MIN_CULTURAL_INDICATORS=3

# Run with environment configuration
python main.py --input data/raw/dreams_500.json --output-dir output/
```

## 📈 Output Formats

### OpenAI Format (openai_format.jsonl)
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Sen uzman bir Türk rüya yorumcususun..."
    },
    {
      "role": "user", 
      "content": "Rüyamda fare gördüm, ne anlama gelir?"
    },
    {
      "role": "assistant",
      "content": "Rüyada fare görmek genellikle..."
    }
  ]
}
```

### Cohere Format (cohere_format.jsonl)
```json
{
  "prompt": "Sen uzman bir Türk rüya yorumcususun...\n\nSoru: Rüyamda fare gördüm, ne anlama gelir?\n\nCevap:",
  "completion": "Rüyada fare görmek genellikle..."
}
```

### Quality Report (quality_report.json)
```json
{
  "processing_summary": {
    "total_processing_time_seconds": 45.2,
    "original_record_count": 500,
    "processed_record_count": 487,
    "data_retention_rate": 97.4
  },
  "output_formats": {
    "openai_records": 487,
    "cohere_records": 487,
    "format_consistency": true
  },
  "quality_metrics": {
    "average_content_length": 245,
    "records_with_tags": 456,
    "html_cleaned_rate": 100.0,
    "cultural_context_preserved": true
  },
  "improvement_indicators": {
    "content_quality_score": "HIGH",
    "format_compliance": "PERFECT",
    "training_readiness": "OPTIMIZED"
  }
}
```

## ⚙️ Configuration

### Environment Variables (`.env` file)

The application uses a comprehensive `.env` file for configuration. All settings have sensible defaults, and command line arguments will override environment settings.

**Create your configuration:**
```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred settings
nano .env
```

**Key configuration options:**

```properties
# Processing Configuration
MIN_CONTENT_LENGTH=100          # Minimum content length for filtering
MAX_CONTENT_LENGTH=5000         # Maximum content length
MIN_CULTURAL_INDICATORS=3       # Required cultural context indicators

# Parallel Processing
MAX_WORKERS=                    # Number of workers (empty = auto-detect)
CHUNK_SIZE=                     # Processing chunk size (empty = auto-calculate)

# Output Control
OUTPUT_DIR=output               # Default output directory
SAVE_PROCESSED_DATA=true        # Save intermediate processed data
SAVE_OPENAI_FORMAT=true         # Generate OpenAI format
SAVE_COHERE_FORMAT=true         # Generate Cohere format
SAVE_QUALITY_REPORT=true        # Generate quality analysis report

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=processing.log         # Log file name

# Quality Control
MIN_QUALITY_SCORE=0.7           # Minimum quality threshold (0.0-1.0)
ENABLE_STRICT_VALIDATION=false  # Enable strict validation
MAX_VALIDATION_ERRORS=10        # Maximum validation errors to report
```

### Command Line Options
The application supports command line arguments that override `.env` settings:

```bash
# Override environment settings with command line arguments
python3 main.py \
    --input dreams_500.json \
    --output-dir custom_output/ \
    --min-content-length 150 \
    --parallel \
    --max-workers 4

# View all available options
python3 main.py --help
```

### Configuration Priority (Highest to Lowest)
1. **Command line arguments** (highest priority)
2. **Environment variables** (`.env` file)
3. **Default values** (lowest priority)

## 📊 Performance Metrics

### Processing Speed
- **Target**: < 1 minute for 500 records
- **Sequential Processing**: 45-60 seconds for 500 records
- **Parallel Processing**: 25-35 seconds for 500 records
- **Optimization**: Automatic worker count optimization

### Quality Improvements
- **Content Quality**: 85%+ average quality score
- **Cultural Context**: 95%+ Turkish cultural indicators
- **Symbol Coverage**: 40+ unique dream symbols
- **Training Readiness**: "Excellent" level optimization
- **Data Retention**: 95%+ records pass quality filters

### Performance Features
- **Parallel Processing**: Multi-threaded execution for large datasets
- **Memory Optimization**: Efficient memory usage patterns  
- **Progress Tracking**: Real-time processing feedback
- **Benchmark Mode**: Performance testing and optimization
- **Selective Output**: Configure which files to generate via `.env`

## 🧪 Validation & Testing

### Quick Validation
```bash
# Validate OpenAI format
python -c "
import json
with open('output/openai_format.jsonl') as f:
    for line in f:
        data = json.loads(line)
        assert 'messages' in data
        print('✅ OpenAI format valid')
        break
"

# Validate Cohere format  
python -c "
import json
with open('output/cohere_format.jsonl') as f:
    for line in f:
        data = json.loads(line)
        assert 'prompt' in data and 'completion' in data
        print('✅ Cohere format valid')
        break
"
```

### Performance Testing
```bash
# Run with benchmark mode
python main.py --input data/raw/dreams_500.json --output-dir output/ --benchmark

# Test parallel vs sequential performance
python main.py --input data/raw/dreams_500.json --output-dir output/ --parallel --benchmark
```

### Output Quality Check
```bash
# Check processed data quality
python -c "
import json
with open('output/quality_report.json') as f:
    report = json.load(f)
    print(f\"Processing time: {report['processing_summary']['total_processing_time_seconds']}s\")
    print(f\"Data retention: {report['processing_summary']['data_retention_rate']}%\")
    print(f\"Quality score: {report['improvement_indicators']['content_quality_score']}\")
"
```

## 🚀 Optimization Features

### Content Enhancement
- **Advanced HTML Cleaning**: Multi-stage BeautifulSoup processing
- **Cultural Preservation**: Turkish dream interpretation context maintained
- **Question Diversity**: 10+ question templates per symbol
- **Answer Optimization**: Content length and structure optimization
- **Symbol Extraction**: Intelligent dream symbol identification and categorization

### Performance Features
- **Parallel Processing**: Multi-threaded execution with dynamic worker management
- **Memory Optimization**: Efficient memory usage for large datasets
- **Streaming Processing**: Incremental processing to reduce memory footprint
- **Auto-optimization**: Automatic parameter tuning based on dataset size
- **Progress Monitoring**: Real-time processing feedback and ETA calculation

### Quality Assurance
- **Multi-stage Validation**: Input validation, processing validation, and output validation
- **Cultural Context Scoring**: Specialized Turkish cultural indicator analysis
- **Format Compliance**: Strict adherence to OpenAI and Cohere format requirements
- **Error Recovery**: Robust error handling and graceful degradation

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Import errors from src modules
```bash
# Solution: Ensure you're in the project root directory
cd turkish-dream-sft-optimizer
python main.py --input data/raw/dreams_500.json --output-dir output/
```

**Issue**: `FileNotFoundError` for input data
```bash
# Solution: Check file path and verify data structure
ls -la data/raw/dreams_500.json
python main.py --input data/raw/dreams_500.json --output-dir output/
```

**Issue**: Performance slower than expected
```bash
# Solution: Enable parallel processing for large datasets
python main.py --input data/raw/dreams_500.json --output-dir output/ --parallel --max-workers 4
```

**Issue**: Memory usage too high
```bash
# Solution: Reduce batch size or increase minimum content length
python main.py --input data/raw/dreams_500.json --output-dir output/ --min-content-length 150
```

### Performance Tuning
```bash
# For optimal performance on large datasets
python main.py \
  --input data/raw/dreams_500.json \
  --output-dir output/ \
  --parallel \
  --max-workers 8 \
  --min-content-length 100 \
  --benchmark
```

### Debug Mode
```bash
# Enable detailed logging for troubleshooting
echo "LOG_LEVEL=DEBUG" >> .env
python3 main.py --input dreams_500.json --output-dir output/

# Or override temporarily
LOG_LEVEL=DEBUG python3 main.py --input dreams_500.json --output-dir output/
```

### Selective Output Generation
```bash
# Configure which outputs to generate in .env file
echo "SAVE_PROCESSED_DATA=false" >> .env  # Skip intermediate data
echo "SAVE_OPENAI_FORMAT=true" >> .env    # Generate OpenAI format only
echo "SAVE_COHERE_FORMAT=false" >> .env   # Skip Cohere format
echo "SAVE_QUALITY_REPORT=true" >> .env   # Generate quality report

python3 main.py --input dreams_500.json --output-dir output/
```

## 📝 Development

## 📝 Development

### Project Structure
The project follows a modular architecture with clear separation of concerns:

- **`src/core/`**: Core business logic and processing
- **`src/formatters/`**: Platform-specific format generation
- **`src/utils/`**: Shared utilities and helpers
- **`docs/`**: Documentation and guides

### Adding New Formatters
```python
# Create custom formatter in src/formatters/
from src.formatters.base import BaseSFTFormatter

class CustomFormatter(BaseSFTFormatter):
    def format_single_record(self, record):
        """Custom implementation for new platform."""
        return {
            "custom_format": "implementation",
            "record": record
        }
```

### Extending Processing Logic
```python
# Extend core processors in src/core/
from src.core.data_processor import DreamDataProcessor

class EnhancedProcessor(DreamDataProcessor):
    def custom_cleaning_step(self, content):
        """Add custom content cleaning logic."""
        # Custom implementation
        return cleaned_content
```

### Adding Utilities
```python
# Create new utilities in src/utils/
from src.utils.logger import setup_logger
from src.utils.env_config import env_config

logger = setup_logger(__name__)

def custom_utility_function():
    """Add custom utility functions."""
    min_length = env_config.min_content_length
    logger.info(f"Using min content length: {min_length}")
    return result
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the project structure
4. Test your changes: `python3 main.py --input dreams_500.json --output-dir test_output/`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open Pull Request

### Development Guidelines
- Follow the modular architecture pattern
- Add appropriate logging and error handling
- Update documentation for new features
- Test with sample data before submitting
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Turkish cultural dream interpretation traditions
- MongoDB document structure optimization
- OpenAI and Cohere fine-tuning best practices
- BeautifulSoup for robust HTML processing
- Python multiprocessing for performance optimization
- python-dotenv for environment configuration management

---

**🎯 Target Achievement**: Optimized SFT dataset preparation with modular architecture, parallel processing, and flexible environment-based configuration.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Turkish cultural dream interpretation traditions
- MongoDB document structure optimization
- OpenAI and Cohere fine-tuning best practices
- BeautifulSoup for robust HTML processing

---

**🎯 Target Achievement**: 70%+ training accuracy improvement through optimized SFT dataset preparation.