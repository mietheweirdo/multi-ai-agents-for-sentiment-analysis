#!/usr/bin/env python3
"""
Data Pipeline Package for Multi-Agent Sentiment Analysis
========================================================

This package provides modular data scraping, preprocessing, and integration
capabilities for the multi-agent sentiment analysis system.

Main Components:
- config: Configuration classes and utilities
- scrapers: YouTube and Tiki data scrapers  
- preprocessor: Advanced data preprocessing and quality filtering
- pipeline: Main pipeline orchestrator
- utils: Utility functions for data handling

Quick Usage:
    from data_pipeline import scrape_and_preprocess
    
    data = scrape_and_preprocess(
        keyword="smartphone",
        sources=['youtube', 'tiki'],
        max_items_per_source=10
    )
"""

from .config import ScrapingConfig, PreprocessingConfig
from .scrapers import YouTubeScraper, TikiScraper
from .preprocessor import AdvancedPreprocessor
from .pipeline import IntegratedDataPipeline, scrape_and_preprocess
from .utils import standardize_for_agents, load_config_from_file

__version__ = "1.0.0"
__author__ = "Multi-Agent Sentiment Analysis Team"

# Main exports
__all__ = [
    # Configuration
    'ScrapingConfig',
    'PreprocessingConfig',
    
    # Scrapers
    'YouTubeScraper', 
    'TikiScraper',
    
    # Preprocessing
    'AdvancedPreprocessor',
    
    # Pipeline
    'IntegratedDataPipeline',
    'scrape_and_preprocess',
    
    # Utilities
    'standardize_for_agents',
    'load_config_from_file'
]
