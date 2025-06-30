"""
Data Pipeline Package for Multi-Agent Sentiment Analysis System
==============================================================

This package provides unified data scraping, preprocessing, and standardization
for the multi-agent sentiment analysis system.
"""

# Import key functions and classes for easy access
try:
    from .scraper import UnifiedScraper, scrape_data_for_keyword
    from .preprocessor import DataPreprocessor, AgentReadyData, preprocess_scraped_data
    
    __all__ = [
        "UnifiedScraper",
        "scrape_data_for_keyword", 
        "DataPreprocessor",
        "AgentReadyData",
        "preprocess_scraped_data"
    ]
    
except ImportError as e:
    print(f"Warning: Some data pipeline components could not be imported: {e}")
    __all__ = []

__version__ = "1.0.0"
