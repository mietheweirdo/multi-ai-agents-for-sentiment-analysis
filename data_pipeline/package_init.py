"""
Data Pipeline Package for Multi-Agent Sentiment Analysis System
==============================================================

This package provides unified data scraping, preprocessing, and standardization
for the multi-agent sentiment analysis system.

Main components:
- scraper.py: Unified scraping from YouTube and Tiki
- preprocessor.py: Advanced preprocessing pipeline
- pipeline.py: Complete end-to-end pipeline

Usage:
    from data_pipeline import get_real_data_for_keyword, get_sample_reviews_for_demo
    
    # Get processed data for a keyword
    data = get_real_data_for_keyword("airpods pro")
    
    # Get sample reviews for demo
    reviews = get_sample_reviews_for_demo("airpods pro", max_samples=5)
"""

from .pipeline import (
    DataPipeline,
    get_real_data_for_keyword,
    get_sample_reviews_for_demo
)

from .scraper import (
    UnifiedScraper,
    scrape_data_for_keyword
)

from .preprocessor import (
    DataPreprocessor,
    AgentReadyData,
    preprocess_scraped_data
)

__version__ = "1.0.0"
__all__ = [
    "DataPipeline",
    "get_real_data_for_keyword", 
    "get_sample_reviews_for_demo",
    "UnifiedScraper",
    "scrape_data_for_keyword",
    "DataPreprocessor", 
    "AgentReadyData",
    "preprocess_scraped_data"
]
