#!/usr/bin/env python3
"""
Configuration classes for the data pipeline
"""

import json
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ScrapingConfig:
    """Configuration for scraping operations"""
    # YouTube settings
    youtube_languages: List[str] = None
    youtube_fallback_auto: bool = True
    youtube_api_key: Optional[str] = None
    youtube_max_videos: int = 5            # Default: 5 videos
    youtube_max_comments: int = 20         # Default: 20 comments per video
    
    # Tiki settings
    tiki_max_reviews_per_product: int = 20
    tiki_max_products: int = 5             # Default: 5 products
    
    # General settings
    output_dir: str = "scraped_data"
    enable_preprocessing: bool = True
    
    def __post_init__(self):
        if self.youtube_languages is None:
            self.youtube_languages = ['vi', 'en']

@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing pipeline"""
    # Quality filtering thresholds
    min_text_length: int = 20
    max_text_length: int = 2000
    min_word_count: int = 3
    max_repetition_ratio: float = 0.8
    
    # Language detection thresholds
    vietnamese_char_threshold: float = 0.05
    english_word_threshold: float = 0.3
    
    # Deduplication settings
    enable_deduplication: bool = True
    similarity_threshold: float = 0.85
    
    # Language detection
    target_language: str = 'vi'  # Vietnamese preferred
    
    # Output settings
    output_dir: str = "preprocessed_data"

def load_config_from_file(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {config_path}: {e}. Using defaults.")
        return {}

def create_scraping_config_from_dict(config_dict: dict) -> ScrapingConfig:
    """Create ScrapingConfig from dictionary"""
    return ScrapingConfig(
        youtube_api_key=config_dict.get('youtube_api_key'),
        youtube_max_videos=config_dict.get('youtube_max_videos', 5),
        youtube_max_comments=config_dict.get('youtube_max_comments', 20),
        tiki_max_products=config_dict.get('tiki_max_products', 5),
        tiki_max_reviews_per_product=config_dict.get('tiki_max_reviews_per_product', 20)
    )
