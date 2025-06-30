#!/usr/bin/env python3
"""
Utility functions for data pipeline
"""

import json
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def standardize_for_agents(processed_data: List[Dict[str, Any]], product_category: str = "general") -> List[Dict[str, Any]]:
    """
    Standardize processed data for sentiment analysis agents.
    This function converts the preprocessed data into the format expected by the agents.
    """
    standardized_items = []
    
    for item in processed_data:
        # Create standardized format for agents
        standardized_item = {
            'review_text': item['content'],
            'product_category': product_category,
            'metadata': {
                'source': item['source'],
                'language': item['language'],
                'original_id': item['id'],
                'created_at': item['created_at'],
                'data_type': item['metadata'].get('data_type'),
                'author': item['metadata'].get('author'),
                'rating': item['metadata'].get('rating'),
                'product_id': item['metadata'].get('product_id'),
                'product_name': item['metadata'].get('product_name'),
                'video_id': item['metadata'].get('video_id'),
                'video_title': item['metadata'].get('video_title'),
                'url': item['metadata'].get('url'),
                'like_count': item['metadata'].get('like_count'),
                'quality_score': 0.8,  # Default quality score
                'timestamp': datetime.now().isoformat()
            }
        }
        
        standardized_items.append(standardized_item)
    
    return standardized_items

def save_data_to_file(data: Any, filepath: str, description: str = "data") -> None:
    """Save data to JSON file with error handling"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"{description.capitalize()} saved to: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save {description} to {filepath}: {e}")

def load_config_from_file(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        logger.warning(f"Config file {config_path} not found. Using defaults.")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {config_path}: {e}. Using defaults.")
        return {}
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}. Using defaults.")
        return {}

def detect_product_category(text: str, product_name: str = "") -> str:
    """Simple product category detection based on keywords"""
    text_lower = (text + " " + product_name).lower()
    
    # Electronics keywords
    electronics_keywords = [
        'phone', 'smartphone', 'laptop', 'computer', 'headphone', 'earphone', 
        'tablet', 'camera', 'speaker', 'tv', 'monitor', 'mouse', 'keyboard',
        'airpods', 'bluetooth', 'wireless', 'usb', 'charger', 'battery'
    ]
    
    # Fashion keywords
    fashion_keywords = [
        'dress', 'shirt', 'pants', 'shoes', 'bag', 'clothes', 'fashion',
        'jacket', 'sweater', 'jeans', 'sneakers', 'boots', 'watch', 'jewelry'
    ]
    
    # Beauty keywords
    beauty_keywords = [
        'makeup', 'cosmetic', 'skincare', 'perfume', 'cream', 'lotion',
        'shampoo', 'conditioner', 'lipstick', 'foundation', 'serum'
    ]
    
    # Home keywords
    home_keywords = [
        'furniture', 'chair', 'table', 'bed', 'sofa', 'kitchen', 'appliance',
        'refrigerator', 'microwave', 'vacuum', 'cleaning', 'decoration'
    ]
    
    # Books keywords
    books_keywords = [
        'book', 'novel', 'textbook', 'manual', 'guide', 'story', 'literature',
        'reading', 'author', 'publisher', 'edition'
    ]
    
    # Check categories
    if any(keyword in text_lower for keyword in electronics_keywords):
        return 'electronics'
    elif any(keyword in text_lower for keyword in fashion_keywords):
        return 'fashion'
    elif any(keyword in text_lower for keyword in beauty_keywords):
        return 'beauty'
    elif any(keyword in text_lower for keyword in home_keywords):
        return 'home'
    elif any(keyword in text_lower for keyword in books_keywords):
        return 'books'
    else:
        return 'general'

def calculate_processing_stats(raw_count: int, processed_count: int, agent_ready_count: int) -> Dict[str, Any]:
    """Calculate processing pipeline statistics"""
    return {
        'raw_data_count': raw_count,
        'processed_data_count': processed_count,
        'agent_ready_count': agent_ready_count,
        'preprocessing_retention_rate': processed_count / raw_count if raw_count > 0 else 0,
        'final_retention_rate': agent_ready_count / raw_count if raw_count > 0 else 0,
        'processing_efficiency': agent_ready_count / processed_count if processed_count > 0 else 0
    }
