#!/usr/bin/env python3
"""
Data Integration Module for Multi-Agent Sentiment Analysis System
===============================================================

Provides functions to replace static test data with real scraped and processed data.
This module integrates with demo_enhanced_system.py and test_langgraph_system.py.

"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_real_reviews_for_demo(keyword: str = "airpods pro", max_reviews: int = 5) -> List[Dict[str, Any]]:
    """
    Get real reviews for demo purposes, with fallback to sample data
    
    Args:
        keyword: Search keyword for scraping
        max_reviews: Maximum number of reviews to return
        
    Returns:
        List of review dictionaries ready for sentiment analysis
    """
    logger.info(f"Getting real reviews for keyword: '{keyword}'")
    
    try:
        # Try to import and use the data pipeline
        from data_pipeline import scrape_data_for_keyword, preprocess_scraped_data
        
        # Scrape fresh data (reduced limits for demo)
        scraped_data = scrape_data_for_keyword(
            keyword, 
            max_youtube_videos=2, 
            max_tiki_products=2
        )
        
        # Preprocess the data
        processed_data = preprocess_scraped_data(scraped_data)
        
        # Convert to demo format
        demo_reviews = []
        for item in processed_data.get('agent_ready_data', [])[:max_reviews]:
            if isinstance(item, dict):
                # Data from JSON/cache
                review = {
                    'text': item['text'],
                    'source': item.get('source', 'unknown'),
                    'product_category': item.get('product_category', 'electronics'),
                    'metadata': {
                        'data_type': item.get('data_type', 'unknown'),
                        'language': item.get('language', 'unknown'),
                        'scraped': True,
                        'keyword': keyword
                    }
                }
            else:
                # AgentReadyData object
                review = {
                    'text': item.text,
                    'source': item.source,
                    'product_category': item.product_category,
                    'metadata': {
                        'data_type': item.data_type,
                        'language': item.language,
                        'scraped': True,
                        'keyword': keyword
                    }
                }
            
            demo_reviews.append(review)
        
        if demo_reviews:
            logger.info(f"Successfully retrieved {len(demo_reviews)} real reviews")
            return demo_reviews
        else:
            logger.warning("No real reviews found, falling back to sample data")
            
    except Exception as e:
        logger.error(f"Failed to get real reviews: {e}")
        logger.info("Falling back to sample data")
    
    # Fallback to sample data
    return get_sample_data_for_demo(keyword, max_reviews)

def get_sample_data_for_demo(keyword: str = "airpods pro", max_reviews: int = 5) -> List[Dict[str, Any]]:
    """
    Get sample data for demo when real data is not available
    
    Args:
        keyword: Keyword for context
        max_reviews: Maximum number of sample reviews
        
    Returns:
        List of sample review dictionaries
    """
    # Create sample data that varies based on keyword
    if "airpods" in keyword.lower() or "headphone" in keyword.lower():
        product_category = "electronics"
        sample_reviews = [
            {
                'text': "Amazing sound quality and battery life! The noise cancellation works perfectly.",
                'source': 'youtube',
                'product_category': product_category,
                'metadata': {'data_type': 'transcript_segment', 'language': 'english', 'scraped': False}
            },
            {
                'text': "Âm thanh tốt nhưng giá hơi cao. Chất lượng xứng đáng với giá tiền.",
                'source': 'tiki',
                'product_category': product_category,
                'metadata': {'data_type': 'product_review', 'language': 'vietnamese', 'scraped': False}
            },
            {
                'text': "Good product but delivery was slow and customer service wasn't helpful.",
                'source': 'tiki',
                'product_category': product_category,
                'metadata': {'data_type': 'product_review', 'language': 'english', 'scraped': False}
            },
            {
                'text': "Perfect for workouts! Stays in place and sweat resistant.",
                'source': 'youtube',
                'product_category': product_category,
                'metadata': {'data_type': 'transcript_segment', 'language': 'english', 'scraped': False}
            },
            {
                'text': "Disappointing battery life and connection issues. Expected better quality.",
                'source': 'youtube',
                'product_category': product_category,
                'metadata': {'data_type': 'transcript_segment', 'language': 'english', 'scraped': False}
            }
        ]
    elif "laptop" in keyword.lower() or "computer" in keyword.lower():
        product_category = "electronics"
        sample_reviews = [
            {
                'text': "Excellent performance for coding and gaming. Fast startup and great display.",
                'source': 'youtube',
                'product_category': product_category,
                'metadata': {'data_type': 'transcript_segment', 'language': 'english', 'scraped': False}
            },
            {
                'text': "Laptop chạy mượt mà, thiết kế đẹp nhưng hơi nóng khi sử dụng lâu.",
                'source': 'tiki',
                'product_category': product_category,
                'metadata': {'data_type': 'product_review', 'language': 'vietnamese', 'scraped': False}
            },
            {
                'text': "Great specs but poor customer support when I had issues.",
                'source': 'tiki',
                'product_category': product_category,
                'metadata': {'data_type': 'product_review', 'language': 'english', 'scraped': False}
            }
        ]
    else:
        # Generic sample data
        product_category = "general"
        sample_reviews = [
            {
                'text': f"Great {keyword}! Excellent quality and fast delivery.",
                'source': 'youtube',
                'product_category': product_category,
                'metadata': {'data_type': 'transcript_segment', 'language': 'english', 'scraped': False}
            },
            {
                'text': f"Sản phẩm {keyword} tốt, chất lượng ổn nhưng giá hơi cao.",
                'source': 'tiki',
                'product_category': product_category,
                'metadata': {'data_type': 'product_review', 'language': 'vietnamese', 'scraped': False}
            },
            {
                'text': f"Mixed feelings about this {keyword}. Good product but poor service.",
                'source': 'tiki',
                'product_category': product_category,
                'metadata': {'data_type': 'product_review', 'language': 'english', 'scraped': False}
            }
        ]
    
    return sample_reviews[:max_reviews]

def get_diverse_test_reviews(keyword: str = "smartphone") -> List[Dict[str, Any]]:
    """
    Get diverse test reviews for comprehensive testing
    
    Args:
        keyword: Product keyword for context
        
    Returns:
        List of diverse reviews for testing different scenarios
    """
    return [
        {
            'text': f"This {keyword} has amazing performance and great screen, but the customer service was terrible and delivery took forever.",
            'source': 'tiki',
            'product_category': 'electronics',
            'metadata': {'scenario': 'mixed_review', 'expected': 'mixed_sentiment'}
        },
        {
            'text': f"Absolutely love this {keyword}! Amazing camera, fast performance, quick delivery, and excellent customer support!",
            'source': 'youtube',
            'product_category': 'electronics',
            'metadata': {'scenario': 'clearly_positive', 'expected': 'positive_sentiment'}
        },
        {
            'text': f"Worst {keyword} ever! Product broke immediately, terrible quality, awful customer service, slow delivery!",
            'source': 'tiki',
            'product_category': 'electronics',
            'metadata': {'scenario': 'clearly_negative', 'expected': 'negative_sentiment'}
        },
        {
            'text': f"Sản phẩm {keyword} rất tốt! Chất lượng tuyệt vời, giao hàng nhanh, hỗ trợ khách hàng chu đáo.",
            'source': 'tiki',
            'product_category': 'electronics',
            'metadata': {'scenario': 'vietnamese_positive', 'expected': 'positive_sentiment'}
        },
        {
            'text': f"The {keyword} quality is good but packaging was damaged and customer service was unhelpful.",
            'source': 'youtube',
            'product_category': 'electronics',
            'metadata': {'scenario': 'quality_vs_service', 'expected': 'mixed_sentiment'}
        }
    ]

def save_scraped_data_sample(keyword: str = "airpods pro", filename: Optional[str] = None):
    """
    Save a sample of scraped data to file for inspection
    
    Args:
        keyword: Keyword to scrape
        filename: Optional filename, defaults to keyword-based name
    """
    if filename is None:
        filename = f"scraped_data_{keyword.replace(' ', '_')}.json"
    
    try:
        reviews = get_real_reviews_for_demo(keyword, max_reviews=10)
        
        data = {
            'keyword': keyword,
            'scraped_at': datetime.now().isoformat(),
            'reviews': reviews,
            'total_reviews': len(reviews),
            'sources': list(set(r.get('source', 'unknown') for r in reviews))
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Scraped data saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to save scraped data: {e}")

def test_data_integration():
    """Test the data integration functionality"""
    print("Testing Data Integration Module")
    print("=" * 50)
    
    # Test real data retrieval
    print("\n1. Testing real data retrieval:")
    reviews = get_real_reviews_for_demo("airpods pro", max_reviews=3)
    print(f"   Retrieved {len(reviews)} reviews")
    for i, review in enumerate(reviews):
        scraped = "REAL" if review['metadata'].get('scraped', False) else "SAMPLE"
        print(f"   {i+1}. [{scraped}][{review['source']}] {review['text'][:50]}...")
    
    # Test diverse test data
    print("\n2. Testing diverse test reviews:")
    test_reviews = get_diverse_test_reviews("smartphone")
    print(f"   Generated {len(test_reviews)} test scenarios")
    for i, review in enumerate(test_reviews):
        scenario = review['metadata']['scenario']
        print(f"   {i+1}. [{scenario}] {review['text'][:50]}...")
    
    # Test sample data generation
    print("\n3. Testing sample data generation:")
    for keyword in ["laptop", "dress", "phone"]:
        samples = get_sample_data_for_demo(keyword, max_reviews=2)
        print(f"   {keyword}: {len(samples)} samples generated")

if __name__ == "__main__":
    test_data_integration()
