# Quick Reference Guide

## 🚀 **Quick Commands**

### Basic Usage
```bash
# Install dependencies
pip install -r requirements_preprocessing.txt

# Run Jupyter notebook (interactive)
jupyter notebook agent_ready_preprocessing.ipynb

# Run standalone script (command line)
python advanced_preprocessing.py
```

### Common Import Patterns
```python
# Essential imports
from advanced_preprocessing import AgentReadyPreprocessor, PreprocessingConfig

# Full imports for advanced usage
from advanced_preprocessing import (
    AgentReadyPreprocessor, 
    BalancedPreprocessor,
    PreprocessingConfig
)
```

## ⚙️ **Configuration Quick Reference**

### Default Configuration
```python
config = PreprocessingConfig()  # Use all defaults
```

### Common Configurations

#### High Quality (Strict)
```python
config = PreprocessingConfig(
    min_text_length=10,
    max_text_length=500,
    min_word_count=3,
    max_repetition_ratio=0.6,
    similarity_threshold=0.9
)
```

#### Balanced (Recommended)
```python
config = PreprocessingConfig(
    min_text_length=5,
    max_text_length=1000,
    min_word_count=2,
    max_repetition_ratio=0.8,
    similarity_threshold=0.85
)
```

#### Permissive (Maximum Retention)
```python
config = PreprocessingConfig(
    min_text_length=1,
    max_text_length=2000,
    min_word_count=1,
    max_repetition_ratio=0.95,
    similarity_threshold=0.7
)
```

## 📁 **File Structure Reference**

### Input Files Format
```json
[
  {
    "text": "Review text content",
    "rating": 5,
    "source": "tiki",
    "timestamp": "2024-01-01"
  }
]
```

### Output Files
- **Main Output**: `agent_ready_sentiment_data_YYYYMMDD_HHMMSS.json`
- **Processing Report**: `preprocessing_report_YYYYMMDD_HHMMSS.txt`
- **Log File**: `preprocessing.log`

## 🔍 **Key Metrics Reference**

### Success Rate Benchmarks
- **Excellent**: >95% success rate
- **Good**: 85-95% success rate  
- **Acceptable**: 75-85% success rate
- **Poor**: <75% success rate (investigate configuration)

### Performance Benchmarks
- **Processing Speed**: ~0.1 seconds per item
- **Memory Usage**: <100MB for 1000 items
- **Accuracy**: 97%+ PII redaction accuracy

## 🛠️ **Troubleshooting Quick Fixes**

### Low Success Rate
```python
# Try more permissive settings
config = PreprocessingConfig(
    min_text_length=1,
    min_word_count=1,
    max_repetition_ratio=0.95
)
```

### Memory Issues
```python
# Process files individually
for file in input_files:
    result = preprocessor.process_files([file])
```

### Encoding Issues
```python
# Ensure UTF-8 encoding
import json
with open('file.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

## 📊 **Output Format Quick Reference**

### Agent-Ready JSON Structure
```json
{
  "preprocessing_metadata": {
    "version": "2.0_LLM_optimized",
    "processing_timestamp": "2025-06-30T03:09:05",
    "total_items": 213,
    "success_rate": 0.9726,
    "processing_time_seconds": 21.5
  },
  "quality_metrics": {
    "average_text_length": 156.8,
    "language_distribution": {
      "vietnamese": 66.2,
      "english": 33.3,
      "mixed": 0.5
    },
    "duplicates_removed": 5,
    "pii_redactions": 12
  },
  "items": [
    {
      "id": "item_001",
      "original_text": "Original review text",
      "processed_text": "Cleaned and normalized text",
      "language": "vietnamese",
      "sentiment_indicators": ["positive", "product_quality"],
      "processing_notes": ["pii_redacted", "normalized"],
      "quality_score": 0.95,
      "metadata": {
        "source": "tiki",
        "rating": 5,
        "timestamp": "2024-01-01"
      }
    }
  ]
}
```

## 🔧 **API Quick Reference**

### Core Methods
```python
# Initialize
preprocessor = AgentReadyPreprocessor(config)

# Process files
result = preprocessor.process_files(file_list)

# Process single text
clean_text = preprocessor.clean_text(raw_text)

# Check quality
is_quality = preprocessor.is_high_quality(text)

# Detect language
language = preprocessor.detect_language(text)
```

### Configuration Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_text_length` | int | 5 | Minimum text length |
| `max_text_length` | int | 1000 | Maximum text length |
| `min_word_count` | int | 2 | Minimum word count |
| `max_repetition_ratio` | float | 0.8 | Max repetition allowed |
| `similarity_threshold` | float | 0.85 | Deduplication threshold |
| `enable_pii_redaction` | bool | True | Enable PII removal |
| `output_dir` | str | "agent_ready_data" | Output directory |

## 🎯 **Best Practices Checklist**

### Before Processing
- ✅ Check input file encoding (UTF-8)
- ✅ Verify JSON format validity
- ✅ Backup original data files
- ✅ Set appropriate configuration for your use case

### During Processing
- ✅ Monitor logs for errors
- ✅ Check memory usage for large datasets
- ✅ Validate success rate meets requirements

### After Processing
- ✅ Review processing report
- ✅ Validate output format
- ✅ Check language distribution
- ✅ Verify PII redaction effectiveness

## 🚨 **Common Error Messages**

### `FileNotFoundError`
```python
# Ensure file paths are correct
import os
for file in input_files:
    if not os.path.exists(file):
        print(f"File not found: {file}")
```

### `UnicodeDecodeError` 
```python
# Force UTF-8 encoding
with open(file, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)
```

### `MemoryError`
```python
# Process in smaller batches
batch_size = 100
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    # Process batch
```

### Low Success Rate
- Check `min_text_length` and `min_word_count` settings
- Review `max_repetition_ratio` threshold  
- Examine input data quality
- Check preprocessing logs for specific failures

## 📞 **Support Resources**

- **Documentation**: See `README.md`, `API_DOCUMENTATION.md`
- **Examples**: See `EXAMPLES.md`
- **Installation**: See `INSTALLATION.md`
- **Contributing**: See `CONTRIBUTING.md`
- **Issues**: Check `preprocessing.log` for detailed error information
