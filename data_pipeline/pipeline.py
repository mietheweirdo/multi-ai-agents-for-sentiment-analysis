#!/usr/bin/env python3
"""
Unified Data Pipeline for Multi-Agent Sentiment Analysis System
=============================================================

Combines scraping, preprocessing, and standardization into a single pipeline.
Replaces static test data with real, processed data from YouTube and Tiki.

"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .scraper import UnifiedScraper, scrape_data_for_keyword
from .preprocessor import DataPreprocessor, AgentReadyData, preprocess_scraped_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipeline:
    """Complete data pipeline from scraping to agent-ready format"""
    
    def __init__(self, 
                 cache_dir: str = "data_cache",
                 max_youtube_videos: int = 5,
                 max_tiki_products: int = 3,
                 enable_caching: bool = True):
        
        self.cache_dir = cache_dir
        self.max_youtube_videos = max_youtube_videos
        self.max_tiki_products = max_tiki_products
        self.enable_caching = enable_caching
        
        # Create cache directory
        if self.enable_caching:
            os.makedirs(cache_dir, exist_ok=True)
        
        logger.info("Data pipeline initialized")
    
    def get_agent_ready_data(self, keyword: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get agent-ready data for a keyword, using cache if available
        
        Args:
            keyword: Search keyword
            force_refresh: If True, bypasses cache and scrapes fresh data
            
        Returns:
            Dictionary containing agent-ready data and metadata
        """
        cache_file = os.path.join(self.cache_dir, f"{keyword.replace(' ', '_')}_processed.json")
        
        # Check cache first
        if not force_refresh and self.enable_caching and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Check if cache is recent (within 24 hours)
                cached_time = datetime.fromisoformat(cached_data.get('processed_at', '2000-01-01'))
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                
                if age_hours < 24:
                    logger.info(f"Using cached data for keyword '{keyword}' (age: {age_hours:.1f} hours)")
                    return cached_data
                else:
                    logger.info(f"Cache expired for keyword '{keyword}' (age: {age_hours:.1f} hours)")
            except Exception as e:
                logger.warning(f"Failed to load cache for keyword '{keyword}': {e}")
        
        # Scrape fresh data
        logger.info(f"Starting fresh data pipeline for keyword: '{keyword}'")
        
        # Step 1: Scrape data
        scraped_data = self._scrape_data(keyword)
        
        # Step 2: Preprocess data
        processed_data = self._preprocess_data(scraped_data)
        
        # Step 3: Add pipeline metadata
        final_data = self._add_pipeline_metadata(processed_data, keyword)
        
        # Step 4: Cache results
        if self.enable_caching:
            self._cache_results(final_data, cache_file)
        
        logger.info(f"Data pipeline completed for keyword '{keyword}'")
        return final_data
    
    def _scrape_data(self, keyword: str) -> Dict[str, Any]:
        """Scrape data from YouTube and Tiki"""
        logger.info(f"Scraping data for keyword: '{keyword}'")
        
        try:
            scraped_data = scrape_data_for_keyword(
                keyword, 
                max_youtube_videos=self.max_youtube_videos,
                max_tiki_products=self.max_tiki_products
            )
            
            total_points = scraped_data['scraping_stats']['total_data_points']
            logger.info(f"Scraped {total_points} data points for keyword '{keyword}'")
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"Scraping failed for keyword '{keyword}': {e}")
            # Return empty data structure
            return {
                'keyword': keyword,
                'timestamp': datetime.now().isoformat(),
                'youtube_data': [],
                'tiki_data': [],
                'scraping_stats': {
                    'youtube_videos_processed': 0,
                    'youtube_comments_collected': 0,
                    'tiki_products_processed': 0,
                    'tiki_reviews_collected': 0,
                    'total_data_points': 0,
                    'scraping_errors': [str(e)]
                }
            }
    
    def _preprocess_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess scraped data for agent consumption"""
        logger.info("Preprocessing scraped data")
        
        try:
            processed_data = preprocess_scraped_data(scraped_data)
            
            processed_count = len(processed_data['agent_ready_data'])
            logger.info(f"Preprocessing completed: {processed_count} agent-ready data points")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            # Return minimal processed structure
            return {
                'keyword': scraped_data.get('keyword', 'unknown'),
                'processed_at': datetime.now().isoformat(),
                'agent_ready_data': [],
                'processing_stats': {
                    'original_data_points': 0,
                    'processed_data_points': 0,
                    'processing_retention_rate': 0,
                    'processing_error': str(e)
                },
                'original_scraping_stats': scraped_data.get('scraping_stats', {})
            }
    
    def _add_pipeline_metadata(self, processed_data: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """Add pipeline-level metadata"""
        processed_data['pipeline_metadata'] = {
            'keyword': keyword,
            'pipeline_version': '1.0.0',
            'pipeline_completed_at': datetime.now().isoformat(),
            'max_youtube_videos': self.max_youtube_videos,
            'max_tiki_products': self.max_tiki_products,
            'data_sources_enabled': ['youtube', 'tiki'],
            'preprocessing_enabled': True,
            'cache_enabled': self.enable_caching
        }
        
        return processed_data
    
    def _cache_results(self, data: Dict[str, Any], cache_file: str):
        """Cache processed results"""
        try:
            # Convert AgentReadyData objects to dictionaries for JSON serialization
            serializable_data = self._make_serializable(data)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results cached to: {cache_file}")
            
        except Exception as e:
            logger.error(f"Failed to cache results: {e}")
    
    def _make_serializable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert AgentReadyData objects to dictionaries for JSON serialization"""
        serializable_data = data.copy()
        
        # Convert AgentReadyData objects to dictionaries
        agent_ready_data = []
        for item in data.get('agent_ready_data', []):
            if isinstance(item, AgentReadyData):
                agent_ready_data.append({
                    'text': item.text,
                    'source': item.source,
                    'data_type': item.data_type,
                    'metadata': item.metadata,
                    'original_rating': item.original_rating,
                    'language': item.language,
                    'product_category': item.product_category
                })
            else:
                agent_ready_data.append(item)
        
        serializable_data['agent_ready_data'] = agent_ready_data
        return serializable_data
    
    def get_sample_reviews_for_demo(self, keyword: str, max_samples: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample reviews formatted for demo purposes
        
        Args:
            keyword: Search keyword
            max_samples: Maximum number of samples to return
            
        Returns:
            List of reviews formatted for demo use
        """
        data = self.get_agent_ready_data(keyword)
        agent_ready_data = data.get('agent_ready_data', [])
        
        # Convert to demo format
        demo_reviews = []
        for i, item in enumerate(agent_ready_data[:max_samples]):
            if isinstance(item, dict):
                # Data loaded from cache
                demo_reviews.append({
                    'text': item['text'],
                    'source': item['source'],
                    'product_category': item.get('product_category', 'general'),
                    'metadata': {
                        'data_type': item.get('data_type'),
                        'language': item.get('language'),
                        'original_rating': item.get('original_rating')
                    }
                })
            else:
                # Fresh AgentReadyData object
                demo_reviews.append({
                    'text': item.text,
                    'source': item.source,
                    'product_category': item.product_category,
                    'metadata': {
                        'data_type': item.data_type,
                        'language': item.language,
                        'original_rating': item.original_rating
                    }
                })
        
        return demo_reviews

def get_real_data_for_keyword(keyword: str, 
                             max_youtube_videos: int = 3, 
                             max_tiki_products: int = 2,
                             force_refresh: bool = False) -> Dict[str, Any]:
    """
    Convenience function to get real data for a keyword
    
    Args:
        keyword: Search keyword
        max_youtube_videos: Maximum YouTube videos to process
        max_tiki_products: Maximum Tiki products to scrape
        force_refresh: Force fresh scraping instead of using cache
        
    Returns:
        Agent-ready data for the keyword
    """
    pipeline = DataPipeline(
        max_youtube_videos=max_youtube_videos,
        max_tiki_products=max_tiki_products
    )
    
    return pipeline.get_agent_ready_data(keyword, force_refresh=force_refresh)

def get_sample_reviews_for_demo(keyword: str, max_samples: int = 5) -> List[Dict[str, Any]]:
    """
    Get sample reviews for demo purposes
    
    Args:
        keyword: Search keyword
        max_samples: Maximum number of samples to return
        
    Returns:
        List of reviews formatted for demo use
    """
    pipeline = DataPipeline()
    return pipeline.get_sample_reviews_for_demo(keyword, max_samples)

if __name__ == "__main__":
    # Test the complete pipeline
    keyword = "airpods pro"
    
    print(f"Testing data pipeline for keyword: '{keyword}'")
    
    # Get processed data
    data = get_real_data_for_keyword(keyword, max_youtube_videos=2, max_tiki_products=1)
    
    print(f"\nPipeline Results:")
    print(f"Keyword: {data['keyword']}")
    print(f"Data points: {len(data['agent_ready_data'])}")
    print(f"Processing stats: {data['processing_stats']}")
    
    # Get sample reviews for demo
    sample_reviews = get_sample_reviews_for_demo(keyword, max_samples=3)
    print(f"\nSample reviews for demo: {len(sample_reviews)}")
    for i, review in enumerate(sample_reviews):
        print(f"  {i+1}. [{review['source']}] {review['text'][:50]}...")
