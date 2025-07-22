# Usage Examples

This document provides practical examples of using the LLM-Ready Preprocessing Pipeline for different scenarios.

## 🚀 Basic Usage Examples

### Example 1: Quick Start with Default Settings

```python
from advanced_preprocessing import AgentReadyPreprocessor, PreprocessingConfig

# Initialize with default configuration
config = PreprocessingConfig()
preprocessor = AgentReadyPreprocessor(config)

# Process your data files
input_files = [
    "tiki_airpod_reviews.json",
    "youtube_airpod_20250629_032359.json"
]

result = preprocessor.process_files(input_files)
print(f"Processing completed! Success rate: {result['success_rate']:.2%}")
```

### Example 2: Custom Configuration for Strict Quality Control

```python
# Configure for high-quality output with strict filtering
strict_config = PreprocessingConfig(
    min_text_length=10,           # Longer minimum text
    max_text_length=500,          # Shorter maximum text  
    min_word_count=3,             # At least 3 words
    max_repetition_ratio=0.6,     # Less repetition allowed
    similarity_threshold=0.9,     # Higher deduplication threshold
    vietnamese_char_threshold=0.1 # More strict Vietnamese detection
)

preprocessor = AgentReadyPreprocessor(strict_config)
result = preprocessor.process_files(input_files)
```

### Example 3: Processing with Privacy-Focused Settings

```python
# Maximum privacy protection
privacy_config = PreprocessingConfig(
    enable_pii_redaction=True,    # Enable PII redaction
    min_text_length=5,
    max_text_length=1000
)

preprocessor = AgentReadyPreprocessor(privacy_config)

# Process files with detailed logging
import logging
logging.basicConfig(level=logging.INFO)

result = preprocessor.process_files(input_files)
print(f"PII redactions performed: {result.get('pii_redactions', 0)}")
```

## 🔍 Advanced Usage Scenarios

### Example 4: Batch Processing with Custom Output Directory

```python
import os
from datetime import datetime

# Create timestamped output directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f"processed_data_{timestamp}"

config = PreprocessingConfig(output_dir=output_dir)
preprocessor = AgentReadyPreprocessor(config)

# Process multiple file sets
file_sets = [
    ["tiki_data_set1.json", "youtube_data_set1.json"],
    ["tiki_data_set2.json", "youtube_data_set2.json"]
]

results = []
for i, files in enumerate(file_sets):
    print(f"Processing batch {i+1}/{len(file_sets)}")
    result = preprocessor.process_files(files)
    results.append(result)
    
total_success_rate = sum(r['success_rate'] for r in results) / len(results)
print(f"Overall success rate: {total_success_rate:.2%}")
```

### Example 5: Language-Specific Processing

```python
# Configure for Vietnamese-heavy content
vietnamese_config = PreprocessingConfig(
    vietnamese_char_threshold=0.02,  # Lower threshold for Vietnamese detection
    english_word_threshold=0.5,      # Higher threshold for English detection
    min_text_length=3                # Shorter minimum for Vietnamese text
)

preprocessor = AgentReadyPreprocessor(vietnamese_config)
result = preprocessor.process_files(["vietnamese_reviews.json"])

# Check language distribution
metadata = result['metadata']
print(f"Vietnamese: {metadata['language_distribution']['vietnamese']}%")
print(f"English: {metadata['language_distribution']['english']}%")
```

## 🧪 Testing and Validation Examples

### Example 6: Custom Quality Validation

```python
def validate_output_quality(output_file):
    """Custom validation function for processed data"""
    import json
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data['items']
    
    # Check for quality metrics
    avg_length = sum(len(item['processed_text']) for item in items) / len(items)
    unique_texts = len(set(item['processed_text'] for item in items))
    
    print(f"Average text length: {avg_length:.1f} characters")
    print(f"Unique texts: {unique_texts}/{len(items)} ({unique_texts/len(items):.2%})")
    
    return {
        'avg_length': avg_length,
        'uniqueness_ratio': unique_texts / len(items),
        'total_items': len(items)
    }

# Process and validate
result = preprocessor.process_files(input_files)
output_file = result['output_file']
quality_metrics = validate_output_quality(output_file)
```

### Example 7: Error Handling and Recovery

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preprocessing_debug.log'),
        logging.StreamHandler()
    ]
)

try:
    config = PreprocessingConfig()
    preprocessor = AgentReadyPreprocessor(config)
    
    # Process with error handling
    result = preprocessor.process_files(input_files)
    
    if result['success_rate'] < 0.8:
        print("Warning: Low success rate detected")
        print("Check preprocessing_debug.log for details")
    
except Exception as e:
    logging.error(f"Processing failed: {e}")
    print("Processing failed - check logs for details")
```

## 📊 Integration Examples

### Example 8: Integration with Sentiment Analysis Pipeline

```python
# Preprocessing for sentiment analysis
def prepare_for_sentiment_analysis(input_files, model_type="llm"):
    """Prepare data specifically for sentiment analysis models"""
    
    if model_type == "llm":
        # LLM-optimized configuration
        config = PreprocessingConfig(
            min_text_length=10,
            max_text_length=512,  # Common LLM context limit
            similarity_threshold=0.85,
            enable_pii_redaction=True
        )
    elif model_type == "bert":
        # BERT-optimized configuration  
        config = PreprocessingConfig(
            min_text_length=5,
            max_text_length=256,  # BERT typical limit
            similarity_threshold=0.9,
            enable_pii_redaction=False  # BERT may handle PII differently
        )
    
    preprocessor = AgentReadyPreprocessor(config)
    result = preprocessor.process_files(input_files)
    
    return result['output_file']

# Usage
llm_ready_file = prepare_for_sentiment_analysis(input_files, "llm")
print(f"Data ready for LLM sentiment analysis: {llm_ready_file}")
```

### Example 9: Data Pipeline Integration

```python
from pathlib import Path
import json

def create_data_pipeline(raw_data_dir, output_base_dir):
    """Complete data pipeline from raw files to processed output"""
    
    # Find all JSON files in raw data directory
    raw_files = list(Path(raw_data_dir).glob("*.json"))
    
    if not raw_files:
        print(f"No JSON files found in {raw_data_dir}")
        return None
    
    # Configure preprocessing
    config = PreprocessingConfig(output_dir=output_base_dir)
    preprocessor = AgentReadyPreprocessor(config)
    
    # Process files
    print(f"Found {len(raw_files)} files to process")
    file_paths = [str(f) for f in raw_files]
    
    result = preprocessor.process_files(file_paths)
    
    # Generate summary report
    summary = {
        'input_files': len(raw_files),
        'success_rate': result['success_rate'],
        'output_file': result['output_file'],
        'processing_time': result.get('processing_time', 'N/A'),
        'total_items_processed': result.get('total_items', 0)
    }
    
    # Save summary
    summary_file = Path(output_base_dir) / "pipeline_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Pipeline completed! Summary saved to {summary_file}")
    return summary

# Usage
summary = create_data_pipeline("raw_social_media_data", "processed_output")
```

## 🎯 Best Practices

### Memory Management for Large Datasets

```python
# For processing very large files
def process_large_dataset(file_path, chunk_size=1000):
    """Process large datasets in chunks to manage memory"""
    import json
    
    config = PreprocessingConfig()
    preprocessor = AgentReadyPreprocessor(config)
    
    # Read and process in chunks
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if len(data) <= chunk_size:
        # Small dataset, process normally
        return preprocessor.process_files([file_path])
    
    # Split into chunks and process
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    results = []
    for i, chunk in enumerate(chunks):
        chunk_file = f"temp_chunk_{i}.json"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f)
        
        result = preprocessor.process_files([chunk_file])
        results.append(result)
        
        # Clean up temporary file
        os.remove(chunk_file)
    
    print(f"Processed {len(chunks)} chunks")
    return results

# Usage for large files
results = process_large_dataset("very_large_dataset.json", chunk_size=500)
```

### Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def performance_timer():
    """Context manager for timing operations"""
    start = time.time()
    yield
    end = time.time()
    print(f"Operation completed in {end - start:.2f} seconds")

# Usage
with performance_timer():
    config = PreprocessingConfig()
    preprocessor = AgentReadyPreprocessor(config)
    result = preprocessor.process_files(input_files)
    
print(f"Processed {result.get('total_items', 0)} items")
print(f"Success rate: {result['success_rate']:.2%}")
```

## 🔧 Troubleshooting Examples

### Common Issues and Solutions

```python
# Issue: Low success rate
def diagnose_low_success_rate(input_files):
    """Diagnose causes of low processing success rate"""
    
    # Try with more lenient settings
    lenient_config = PreprocessingConfig(
        min_text_length=1,
        max_text_length=2000,
        min_word_count=1,
        max_repetition_ratio=0.95,
        similarity_threshold=0.7
    )
    
    preprocessor = AgentReadyPreprocessor(lenient_config)
    
    # Enable detailed logging
    import logging
    logging.getLogger('advanced_preprocessing').setLevel(logging.DEBUG)
    
    result = preprocessor.process_files(input_files)
    
    print(f"Lenient processing success rate: {result['success_rate']:.2%}")
    print("Check logs for specific failure reasons")
    
    return result

# Usage when experiencing issues
result = diagnose_low_success_rate(input_files)
```

These examples cover the most common use cases and should help users get started quickly with the preprocessing pipeline!
