# API Documentation

## Core Classes

### PreprocessingConfig

Configuration dataclass for the preprocessing pipeline.

```python
@dataclass
class PreprocessingConfig:
    """Configuration for LLM preprocessing pipeline"""
    
    # Quality filtering thresholds
    min_text_length: int = 5
    max_text_length: int = 1000
    min_word_count: int = 2
    max_repetition_ratio: float = 0.8
    
    # Language detection thresholds
    vietnamese_char_threshold: float = 0.05
    english_word_threshold: float = 0.3
    
    # Deduplication settings
    similarity_threshold: float = 0.85
    ngram_size: int = 3
    
    # Privacy settings
    enable_pii_redaction: bool = True
    
    # Output settings
    output_dir: str = "agent_ready_data"
```

#### Parameters

- **min_text_length** (int): Minimum text length for quality filtering. Default: 5
- **max_text_length** (int): Maximum text length for quality filtering. Default: 1000
- **min_word_count** (int): Minimum word count for quality filtering. Default: 2
- **max_repetition_ratio** (float): Maximum allowed repetition ratio (0.0-1.0). Default: 0.8
- **vietnamese_char_threshold** (float): Threshold for Vietnamese character detection. Default: 0.05
- **english_word_threshold** (float): Threshold for English word detection. Default: 0.3
- **similarity_threshold** (float): N-gram similarity threshold for deduplication. Default: 0.85
- **ngram_size** (int): N-gram size for similarity calculation. Default: 3
- **enable_pii_redaction** (bool): Enable PII redaction. Default: True
- **output_dir** (str): Output directory path. Default: "agent_ready_data"

### AgentReadyPreprocessor

Main preprocessing class implementing the complete LLM optimization pipeline.

```python
class AgentReadyPreprocessor:
    """LLM-optimized preprocessing pipeline"""
    
    def __init__(self, config: PreprocessingConfig):
        """Initialize preprocessor with configuration"""
        
    def process_dataset(self, file_paths: List[str]) -> str:
        """Process multiple files and return output path"""
        
    def process_single_item(self, text: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single text item through the pipeline"""
```

#### Methods

##### `__init__(config: PreprocessingConfig)`

Initialize the preprocessor with the given configuration.

**Parameters:**
- **config** (PreprocessingConfig): Configuration object

##### `process_dataset(file_paths: List[str]) -> str`

Process multiple JSON files through the complete pipeline.

**Parameters:**
- **file_paths** (List[str]): List of input JSON file paths

**Returns:**
- **str**: Path to the generated agent-ready JSON file

**Example:**
```python
preprocessor = AgentReadyPreprocessor(config)
output_path = preprocessor.process_dataset([
    "tiki_reviews.json",
    "youtube_comments.json"
])
```

##### `process_single_item(text: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]`

Process a single text item through the preprocessing pipeline.

**Parameters:**
- **text** (str): Input text to process
- **metadata** (Dict[str, Any]): Item metadata

**Returns:**
- **Optional[Dict[str, Any]]**: Processed item or None if filtered out

**Example:**
```python
item = preprocessor.process_single_item(
    text="sp này dc ko ae?",
    metadata={"source": "tiki", "product_name": "AirPods"}
)
```

##### `quality_filter(text: str, metadata: Dict[str, Any]) -> Tuple[bool, str]`

Apply quality filtering to text.

**Parameters:**
- **text** (str): Text to filter
- **metadata** (Dict[str, Any]): Item metadata

**Returns:**
- **Tuple[bool, str]**: (passed_filter, reason)

##### `deduplicate(texts: List[str]) -> List[int]`

Perform multi-level deduplication on text list.

**Parameters:**
- **texts** (List[str]): List of texts to deduplicate

**Returns:**
- **List[int]**: Indices of unique texts

##### `redact_pii(text: str) -> str`

Remove personally identifiable information from text.

**Parameters:**
- **text** (str): Text to redact

**Returns:**
- **str**: Text with PII redacted

##### `normalize_text(text: str) -> str`

Apply text normalization (Unicode NFKC, whitespace, etc.).

**Parameters:**
- **text** (str): Text to normalize

**Returns:**
- **str**: Normalized text

##### `detect_language(text: str) -> Tuple[str, float]`

Detect text language with confidence scoring.

**Parameters:**
- **text** (str): Text to analyze

**Returns:**
- **Tuple[str, float]**: (language_code, confidence)

##### `expand_abbreviations(text: str, language: str) -> str`

Expand abbreviations based on language context.

**Parameters:**
- **text** (str): Text with abbreviations
- **language** (str): Language code ('vi' or 'en')

**Returns:**
- **str**: Text with abbreviations expanded

## Data Structures

### Input Data Formats

#### Tiki Format
```json
{
  "product_name": [
    {
      "content": "Review text here"
    }
  ]
}
```

#### YouTube Format
```json
[
  {
    "video_title": "Video title",
    "content": "Comment text here"
  }
]
```

### Output Data Format

#### Agent-Ready JSON
```json
{
  "preprocessing_metadata": {
    "version": "2.0_LLM_optimized",
    "processing_timestamp": "2025-06-30T03:09:05.123456",
    "total_items": 213,
    "preprocessing_pipeline": [
      "quality_filtering",
      "multi_level_deduplication", 
      "privacy_redaction",
      "text_normalization",
      "language_detection",
      "abbreviation_expansion"
    ],
    "config": {
      "min_text_length": 5,
      "max_text_length": 1000,
      "similarity_threshold": 0.85,
      "privacy_redaction_enabled": true
    }
  },
  "quality_metrics": {
    "total_loaded": 219,
    "successfully_processed": 213,
    "quality_filtered": 3,
    "duplicates_removed": 2,
    "privacy_redactions": 7,
    "processing_errors": 0,
    "success_rate": 97.26
  },
  "data_distribution": {
    "source_distribution": {
      "tiki": 69,
      "youtube": 150
    },
    "language_distribution": {
      "vi": 141,
      "en": 71,
      "mixed": 1
    }
  },
  "sentiment_analysis_ready_data": [
    {
      "id": 1,
      "original_text": "Original text",
      "cleaned_text": "Cleaned and processed text",
      "language": "vi",
      "language_confidence": 0.85,
      "processing_steps": {
        "quality_filter": "passed",
        "privacy_redaction": "applied",
        "text_normalization": "applied",
        "language_detection": "vi (0.85)",
        "abbreviation_expansion": "applied"
      },
      "metadata": {
        "source": "tiki",
        "product_name": "Product name"
      }
    }
  ]
}
```

## Error Handling

### Common Exceptions

#### FileNotFoundError
Raised when input files cannot be found.

```python
try:
    output_path = preprocessor.process_dataset(["missing_file.json"])
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

#### JSONDecodeError
Raised when input files contain invalid JSON.

```python
import json
try:
    output_path = preprocessor.process_dataset(["invalid.json"])
except json.JSONDecodeError as e:
    print(f"Invalid JSON format: {e}")
```

### Error Recovery

The preprocessor includes robust error handling:
- Individual item processing errors don't stop the pipeline
- Detailed error logging for debugging
- Graceful degradation for unsupported formats
- Statistics tracking for error analysis

## Performance Considerations

### Memory Usage
- **Small datasets** (<1K items): ~10MB RAM
- **Medium datasets** (1K-10K items): ~50-100MB RAM  
- **Large datasets** (>10K items): Consider batch processing

### Processing Speed
- **Average**: 0.1 seconds per item
- **Batch processing**: ~1000 items per minute
- **I/O bound**: File reading/writing is the bottleneck

### Optimization Tips
1. Use SSD storage for faster I/O
2. Increase batch size for large datasets
3. Disable PII redaction if not needed
4. Adjust similarity threshold for speed vs. accuracy

## Integration Examples

### With Pandas
```python
import pandas as pd
import json

# Load preprocessed data
with open('output.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data['sentiment_analysis_ready_data'])
print(df[['cleaned_text', 'language', 'language_confidence']].head())
```

### With Transformers
```python
from transformers import pipeline

# Load sentiment analysis model
sentiment_pipeline = pipeline("sentiment-analysis")

# Process data
for item in data['sentiment_analysis_ready_data']:
    result = sentiment_pipeline(item['cleaned_text'])
    print(f"Text: {item['cleaned_text'][:50]}...")
    print(f"Sentiment: {result[0]['label']} ({result[0]['score']:.3f})")
```

### With Custom Models
```python
# Custom Vietnamese sentiment model
def analyze_vietnamese_sentiment(text):
    # Your Vietnamese model logic here
    return {"sentiment": "positive", "confidence": 0.85}

# Process by language
for item in data['sentiment_analysis_ready_data']:
    if item['language'] == 'vi':
        result = analyze_vietnamese_sentiment(item['cleaned_text'])
    else:
        result = sentiment_pipeline(item['cleaned_text'])
```
