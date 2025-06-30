# Multi-Agent Sentiment Analysis - API Documentation

## 🔌 **Core API Reference**

### **IntegratedDataPipeline Class**

The main entry point for data scraping and preprocessing.

```python
from integrated_data_pipeline import IntegratedDataPipeline, ScrapingConfig, PreprocessingConfig

# Initialize with custom configuration
pipeline = IntegratedDataPipeline(
    scraping_config=ScrapingConfig(
        youtube_api_key="your-youtube-api-key",
        youtube_max_videos=10,
        youtube_max_comments=50,
        tiki_max_products=5,
        tiki_max_reviews_per_product=100
    ),
    preprocessing_config=PreprocessingConfig(
        min_content_length=20,
        max_content_length=2000,
        enable_deduplication=True
    )
)
```

#### **Methods**

##### `scrape_by_keyword(keyword: str, sources: List[str] = None) -> List[Dict]`
Scrape data from multiple sources using a keyword.

**Parameters:**
- `keyword` (str): Search keyword for finding relevant content
- `sources` (List[str], optional): Sources to scrape from ['youtube', 'tiki']. Default: both

**Returns:**
- `List[Dict]`: Raw scraped data with metadata

**Example:**
```python
raw_data = pipeline.scrape_by_keyword(
    keyword="smartphone camera quality",
    sources=['youtube', 'tiki']
)
print(f"Scraped {len(raw_data)} items from {len(set(item['source'] for item in raw_data))} sources")
```

##### `scrape_by_urls(youtube_urls: List[str] = None, tiki_urls: List[str] = None) -> List[Dict]`
Scrape data from specific URLs.

**Parameters:**
- `youtube_urls` (List[str], optional): List of YouTube video URLs
- `tiki_urls` (List[str], optional): List of Tiki product URLs

**Returns:**
- `List[Dict]`: Raw scraped data

**Example:**
```python
raw_data = pipeline.scrape_by_urls(
    youtube_urls=[
        "https://www.youtube.com/watch?v=VIDEO_ID_1",
        "https://www.youtube.com/watch?v=VIDEO_ID_2"
    ],
    tiki_urls=[
        "https://tiki.vn/tai-nghe-bluetooth-apple-airpods-pro-2-usb-c-mtjv3zp-a-p273150134.html"
    ]
)
```

##### `run_full_pipeline(keyword: str = None, **kwargs) -> Dict`
Execute the complete scraping and preprocessing pipeline.

**Parameters:**
- `keyword` (str, optional): Search keyword
- `youtube_urls` (List[str], optional): YouTube video URLs
- `tiki_urls` (List[str], optional): Tiki product URLs
- `sources` (List[str], optional): Sources to scrape from
- `product_category` (str): Product category for analysis context

**Returns:**
- `Dict`: Complete pipeline results with raw data, processed data, and agent-ready data

**Example:**
```python
result = pipeline.run_full_pipeline(
    keyword="wireless headphones",
    sources=['youtube', 'tiki'],
    product_category="electronics"
)

print(f"Raw data: {len(result['raw_data'])} items")
print(f"Processed data: {len(result['processed_data'])} items") 
print(f"Agent-ready data: {len(result['agent_ready_data'])} items")
print(f"Stats: {result['preprocessing_stats']}")
```

---

### **Convenience Functions**

##### `scrape_and_preprocess(keyword: str = None, **kwargs) -> List[Dict]`
Quick function to scrape and preprocess data in one call.

**Parameters:**
- `keyword` (str, optional): Search keyword
- `youtube_urls` (List[str], optional): YouTube video URLs
- `tiki_urls` (List[str], optional): Tiki product URLs
- `product_category` (str): Product category
- `sources` (List[str], optional): Sources to scrape from
- `max_items_per_source` (int, optional): Limit items per source
- `pipeline` (IntegratedDataPipeline, optional): Custom pipeline instance

**Returns:**
- `List[Dict]`: Agent-ready data items

**Example:**
```python
from integrated_data_pipeline import scrape_and_preprocess

# Simple usage with automatic configuration
data = scrape_and_preprocess(
    keyword="gaming laptop", 
    sources=['tiki'],
    max_items_per_source=20
)

# Each item in data has format:
# {
#     "review_text": "cleaned review content",
#     "product_category": "electronics", 
#     "metadata": {
#         "source": "tiki",
#         "original_id": "123456",
#         "url": "https://tiki.vn/...",
#         "timestamp": "2025-07-01T10:30:00",
#         "language": "vi",
#         "quality_score": 0.89
#     }
# }
```

---

## 🤖 **Agent Analysis APIs**

### **3-Layer Demo System**

```python
from workflow_manager import analyze_review

# Analyze with 3-layer system
result = analyze_review(
    review="This laptop has amazing performance but terrible customer service.",
    product_category="electronics"
)

# Result structure:
{
    "review_text": "original review",
    "product_category": "electronics",
    "department_analyses": [
        {
            "agent_type": "quality",
            "sentiment": "positive",
            "confidence": 0.89,
            "reasoning": "High performance mentioned",
            "key_factors": ["performance", "build quality"]
        },
        {
            "agent_type": "experience", 
            "sentiment": "negative",
            "confidence": 0.92,
            "reasoning": "Terrible customer service mentioned",
            "key_factors": ["customer service", "support"]
        }
        # ... other departments
    ],
    "master_analysis": {
        "sentiment": "mixed",
        "confidence": 0.78,
        "reasoning": "Positive product quality but negative service experience"
    },
    "business_recommendations": {
        "business_impact": "Focus on improving customer service while maintaining product quality",
        "confidence": 0.85,
        "reasoning": "Service improvements could significantly boost satisfaction"
    },
    "workflow_metadata": {
        "processing_time": 3.2,
        "total_departments": 5,
        "workflow_version": "demo"
    }
}
```

### **LangGraph System**

```python
from agents.langgraph_coordinator import analyze_with_langgraph

# Analyze with LangGraph discussion system
result = analyze_with_langgraph(
    review="Mixed feelings about this product - great features but overpriced.",
    product_category="electronics",
    config={"api_key": "your-openai-key"},
    max_discussion_rounds=3,
    disagreement_threshold=0.6
)

# Additional LangGraph-specific fields:
{
    # ... same as 3-layer system, plus:
    "discussion_messages": [
        {
            "round": 1,
            "agent": "quality",
            "message": "I believe this is positive because great features are mentioned",
            "timestamp": "2025-07-01T10:30:00"
        },
        {
            "round": 1, 
            "agent": "business",
            "message": "But overpriced suggests negative business impact",
            "timestamp": "2025-07-01T10:30:05"
        }
        # ... full discussion transcript
    ],
    "workflow_metadata": {
        # ... standard fields, plus:
        "discussion_rounds": 2,
        "disagreement_level": 0.7,
        "consensus_reached": True,
        "workflow_version": "langgraph"
    }
}
```

---

## ⚙️ **Configuration Classes**

### **ScrapingConfig**

```python
from integrated_data_pipeline import ScrapingConfig

config = ScrapingConfig(
    # YouTube settings
    youtube_languages=['vi', 'en'],           # Preferred transcript languages
    youtube_fallback_auto=True,               # Use auto-generated if manual unavailable
    youtube_api_key="your-youtube-api-key",   # YouTube Data API v3 key
    youtube_max_videos=5,                     # Max videos per keyword search
    youtube_max_comments=30,                  # Max comments per video
    
    # Tiki settings  
    tiki_max_reviews_per_product=50,          # Max reviews per product
    tiki_max_products=3,                      # Max products per keyword search
    
    # General settings
    output_dir="scraped_data",                # Directory for raw data files
    enable_preprocessing=True                 # Enable preprocessing pipeline
)
```

### **PreprocessingConfig**

```python
from integrated_data_pipeline import PreprocessingConfig

config = PreprocessingConfig(
    # Quality filtering thresholds
    min_content_length=20,                    # Minimum text length
    max_content_length=2000,                  # Maximum text length  
    min_word_count=3,                         # Minimum word count
    max_repetition_ratio=0.8,                 # Maximum repetition allowed
    
    # Language detection thresholds
    vietnamese_char_threshold=0.05,           # Min Vietnamese chars for VI detection
    english_word_threshold=0.3,               # Min English ratio for EN detection
    
    # Deduplication settings
    enable_deduplication=True,                # Enable duplicate removal
    similarity_threshold=0.85,                # Similarity threshold for duplicates
    
    # Language preferences
    target_language='vi',                     # Preferred language (Vietnamese)
    
    # Output settings
    output_dir="preprocessed_data"            # Directory for processed data
)
```

---

## 🔄 **Batch Processing APIs**

### **Process Multiple Keywords**

```python
from integrated_data_pipeline import scrape_and_preprocess
from workflow_manager import analyze_review

# Batch process multiple keywords
keywords = ["smartphone", "laptop", "headphones", "camera"]
all_results = []

for keyword in keywords:
    print(f"Processing: {keyword}")
    
    # Scrape data for keyword
    data = scrape_and_preprocess(
        keyword=keyword,
        sources=['tiki'],
        max_items_per_source=10
    )
    
    # Analyze each review
    keyword_results = []
    for item in data:
        analysis = analyze_review(
            review=item['review_text'],
            product_category=item['product_category']
        )
        
        keyword_results.append({
            "keyword": keyword,
            "review": item['review_text'][:100] + "...",
            "sentiment": analysis['master_analysis']['sentiment'],
            "confidence": analysis['master_analysis']['confidence'],
            "source": item['metadata']['source']
        })
    
    all_results.extend(keyword_results)

# Aggregate results
sentiment_summary = {}
for result in all_results:
    keyword = result['keyword']
    sentiment = result['sentiment']
    
    if keyword not in sentiment_summary:
        sentiment_summary[keyword] = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    sentiment_summary[keyword][sentiment] += 1

print("\nSentiment Summary by Keyword:")
for keyword, sentiments in sentiment_summary.items():
    total = sum(sentiments.values())
    print(f"{keyword}: {sentiments} (total: {total})")
```

### **Monitor Product Over Time**

```python
import schedule
import time
from datetime import datetime
import json

def monitor_product_sentiment(product_name):
    """Monitor a specific product's sentiment over time"""
    
    # Scrape latest reviews
    data = scrape_and_preprocess(
        keyword=product_name,
        sources=['tiki', 'youtube'],
        max_items_per_source=20
    )
    
    # Analyze sentiment
    results = []
    for item in data:
        analysis = analyze_review(item['review_text'])
        results.append({
            "timestamp": datetime.now().isoformat(),
            "product": product_name,
            "sentiment": analysis['master_analysis']['sentiment'],
            "confidence": analysis['master_analysis']['confidence'],
            "source": item['metadata']['source'],
            "review_snippet": item['review_text'][:100]
        })
    
    # Save to monitoring log
    filename = f"sentiment_monitoring_{product_name.replace(' ', '_')}.json"
    try:
        with open(filename, 'r') as f:
            historical_data = json.load(f)
    except FileNotFoundError:
        historical_data = []
    
    historical_data.extend(results)
    
    with open(filename, 'w') as f:
        json.dump(historical_data, f, indent=2, ensure_ascii=False)
    
    print(f"Monitored {len(results)} reviews for {product_name}")
    
    # Calculate trend
    if len(historical_data) >= 10:
        recent_sentiments = [r['sentiment'] for r in historical_data[-10:]]
        positive_ratio = recent_sentiments.count('positive') / len(recent_sentiments)
        print(f"Recent positive sentiment ratio: {positive_ratio:.2f}")

# Schedule monitoring
schedule.every(6).hours.do(monitor_product_sentiment, "iPhone 15")
schedule.every(6).hours.do(monitor_product_sentiment, "Samsung Galaxy S24")

# Run monitoring loop
while True:
    schedule.run_pending() 
    time.sleep(60)
```

---

## 🔍 **Advanced Usage Patterns**

### **Custom Agent Integration**

```python
from integrated_data_pipeline import scrape_and_preprocess
from agents.langgraph_coordinator import LangGraphCoordinator

# Create custom agent workflow
coordinator = LangGraphCoordinator(
    config={"api_key": "your-key"},
    product_category="electronics",
    department_types=["quality", "technical", "business"],  # Custom agent selection
    max_discussion_rounds=3,
    disagreement_threshold=0.5
)

# Process scraped data with custom workflow
data = scrape_and_preprocess(keyword="gaming mouse")

for item in data[:5]:  # Process first 5 items
    result = coordinator.run_analysis(item['review_text'])
    
    print(f"Review: {item['review_text'][:50]}...")
    print(f"Final Sentiment: {result['master_analysis']['sentiment']}")
    
    if result.get('discussion_messages'):
        print(f"Discussion rounds: {result['workflow_metadata']['discussion_rounds']}")
        print("Key discussion points:")
        for msg in result['discussion_messages'][:3]:  # Show first 3 messages
            print(f"  {msg['agent']}: {msg['message'][:60]}...")
    print("-" * 50)
```

### **Error Handling & Fallbacks**

```python
from integrated_data_pipeline import scrape_and_preprocess
import logging

# Configure comprehensive error handling
logging.basicConfig(level=logging.INFO)

def robust_sentiment_analysis(keyword, fallback_text=None):
    """Perform sentiment analysis with comprehensive error handling"""
    
    try:
        # Try dynamic data scraping
        data = scrape_and_preprocess(
            keyword=keyword,
            sources=['youtube', 'tiki'],
            max_items_per_source=10
        )
        
        if not data:
            raise ValueError("No data scraped")
            
        print(f"✅ Successfully scraped {len(data)} items")
        return data
        
    except Exception as scraping_error:
        print(f"⚠️ Scraping failed: {scraping_error}")
        
        if fallback_text:
            print("Using fallback text for analysis")
            return [{
                'review_text': fallback_text,
                'product_category': 'general',
                'metadata': {
                    'source': 'fallback',
                    'timestamp': datetime.now().isoformat()
                }
            }]
        else:
            raise Exception("No fallback available and scraping failed")

# Usage with fallback
try:
    data = robust_sentiment_analysis(
        keyword="premium headphones",
        fallback_text="These headphones have great sound quality but are expensive."
    )
    
    # Process with either scraped or fallback data
    for item in data:
        analysis = analyze_review(item['review_text'])
        print(f"Sentiment: {analysis['master_analysis']['sentiment']}")
        
except Exception as e:
    print(f"❌ Complete failure: {e}")
```

### **Performance Optimization**

```python
from concurrent.futures import ThreadPoolExecutor
from integrated_data_pipeline import scrape_and_preprocess
import time

def parallel_keyword_analysis(keywords, max_workers=3):
    """Analyze multiple keywords in parallel for better performance"""
    
    def analyze_keyword(keyword):
        start_time = time.time()
        
        try:
            data = scrape_and_preprocess(
                keyword=keyword,
                sources=['tiki'],  # Faster than YouTube
                max_items_per_source=5  # Limit for speed
            )
            
            processing_time = time.time() - start_time
            
            return {
                'keyword': keyword,
                'items_scraped': len(data),
                'processing_time': processing_time,
                'status': 'success',
                'data': data
            }
            
        except Exception as e:
            return {
                'keyword': keyword,
                'items_scraped': 0,
                'processing_time': time.time() - start_time,
                'status': 'failed',
                'error': str(e)
            }
    
    # Execute in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(analyze_keyword, keywords))
    
    # Summary statistics
    total_items = sum(r['items_scraped'] for r in results)
    total_time = max(r['processing_time'] for r in results)  # Parallel time
    success_rate = sum(1 for r in results if r['status'] == 'success') / len(results)
    
    print(f"Parallel Analysis Complete:")
    print(f"  Keywords processed: {len(keywords)}")
    print(f"  Total items scraped: {total_items}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Success rate: {success_rate:.2%}")
    
    return results

# Example usage
keywords = ["smartphone", "laptop", "tablet", "smartwatch", "earbuds"]
results = parallel_keyword_analysis(keywords, max_workers=3)

for result in results:
    if result['status'] == 'success':
        print(f"✅ {result['keyword']}: {result['items_scraped']} items in {result['processing_time']:.2f}s")
    else:
        print(f"❌ {result['keyword']}: {result['error']}")
```

---

## 🐛 **Debugging & Troubleshooting**

### **Enable Debug Logging**

```python
import logging
from integrated_data_pipeline import scrape_and_preprocess

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# This will show detailed scraping progress
data = scrape_and_preprocess(keyword="debug test", sources=['tiki'])
```

### **Common Error Solutions**

```python
from integrated_data_pipeline import scrape_and_preprocess
from googleapiclient.errors import HttpError

def handle_common_errors():
    try:
        data = scrape_and_preprocess(keyword="test", sources=['youtube'])
        
    except HttpError as e:
        if e.resp.status == 403:
            print("❌ YouTube API quota exceeded or invalid key")
            print("💡 Solution: Check API key or wait for quota reset")
        elif e.resp.status == 404:
            print("❌ Video not found or comments disabled")
            print("💡 Solution: Try different keywords or videos")
            
    except ImportError as e:
        print("❌ Missing dependency")
        print("💡 Solution: pip install google-api-python-client")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Solution: Check network connection and configuration")

handle_common_errors()
```

This comprehensive API documentation covers all the main interfaces and usage patterns for the multi-agent sentiment analysis system. Users can reference this for both basic usage and advanced integration scenarios.
