#!/usr/bin/env python3
"""
Data Preprocessing Pipeline for Multi-Agent Sentiment Analysis System
===================================================================

Integrates advanced preprocessing functionality for scraped data.
Prepares data for consumption by sentiment analysis agents.

"""

import json
import os
import sys
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Add the test_thesis path to import advanced_preprocessing
test_thesis_path = r"c:\Users\DELL\Downloads\test_thesis"
if test_thesis_path not in sys.path:
    sys.path.append(test_thesis_path)

try:
    from advanced_preprocessing import AdvancedPreprocessor, PreprocessingConfig
except ImportError as e:
    logging.error(f"Failed to import advanced_preprocessing: {e}")
    # Fallback: Define basic classes
    @dataclass
    class PreprocessingConfig:
        min_text_length: int = 5
        max_text_length: int = 1000
        min_word_count: int = 2
        max_repetition_ratio: float = 0.8
        vietnamese_char_threshold: float = 0.05
        english_word_threshold: float = 0.3
        similarity_threshold: float = 0.85
        ngram_size: int = 3
        enable_pii_redaction: bool = True
        output_dir: str = "preprocessed_data"
        agent_ready_format: bool = True
    
    class AdvancedPreprocessor:
        def __init__(self, config):
            self.config = config
            
        def process_dataset(self, data):
            # Basic fallback processing
            return {"processed_data": data, "stats": {}}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass 
class AgentReadyData:
    """Standardized data format for sentiment analysis agents"""
    text: str
    source: str  # 'youtube' or 'tiki'
    data_type: str  # 'transcript_segment' or 'product_review'
    metadata: Dict[str, Any]
    original_rating: Optional[float] = None
    language: str = "unknown"
    product_category: str = "general"

class DataPreprocessor:
    """Preprocessing pipeline that prepares scraped data for agent consumption"""
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        if config is None:
            config = PreprocessingConfig(
                min_text_length=10,
                max_text_length=800,
                min_word_count=3,
                enable_pii_redaction=True,
                agent_ready_format=True
            )
        
        self.config = config
        self.preprocessor = AdvancedPreprocessor(config)
        
        logger.info("Data preprocessor initialized")
    
    def process_scraped_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process scraped data from YouTube and Tiki into agent-ready format
        
        Args:
            scraped_data: Output from UnifiedScraper
            
        Returns:
            Processed and standardized data ready for sentiment agents
        """
        logger.info(f"Processing scraped data for keyword: {scraped_data.get('keyword', 'unknown')}")
        
        # Extract all text data for preprocessing
        raw_texts = self._extract_raw_texts(scraped_data)
        
        # Apply advanced preprocessing
        preprocessed_data = self._apply_advanced_preprocessing(raw_texts)
        
        # Convert to agent-ready format
        agent_ready_data = self._convert_to_agent_format(scraped_data, preprocessed_data)
        
        # Add processing metadata
        result = {
            'keyword': scraped_data.get('keyword', 'unknown'),
            'processed_at': datetime.now().isoformat(),
            'agent_ready_data': agent_ready_data,
            'processing_stats': self._calculate_processing_stats(scraped_data, agent_ready_data),
            'original_scraping_stats': scraped_data.get('scraping_stats', {}),
            'preprocessing_config': {
                'min_text_length': self.config.min_text_length,
                'max_text_length': self.config.max_text_length,
                'pii_redaction_enabled': self.config.enable_pii_redaction,
                'quality_filtering_enabled': True
            }
        }
        
        logger.info(f"Processing completed. {len(agent_ready_data)} data points ready for agents.")
        
        return result
    
    def _extract_raw_texts(self, scraped_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all text content from scraped data"""
        raw_texts = []
        
        # Process YouTube data
        for video in scraped_data.get('youtube_data', []):
            for comment in video.get('comments', []):
                raw_texts.append({
                    'text': comment.get('text', ''),
                    'source': 'youtube',
                    'source_id': video.get('video_id', 'unknown'),
                    'data_type': comment.get('type', 'transcript_segment'),
                    'original_data': comment,
                    'video_metadata': video.get('metadata', {})
                })
        
        # Process Tiki data
        for product in scraped_data.get('tiki_data', []):
            for review in product.get('reviews', []):
                raw_texts.append({
                    'text': review.get('text', ''),
                    'source': 'tiki',
                    'source_id': product.get('product_id', 'unknown'),
                    'data_type': review.get('type', 'product_review'),
                    'original_rating': review.get('rating'),
                    'original_data': review,
                    'product_metadata': {
                        'product_name': product.get('product_name', ''),
                        'product_category': product.get('product_category', 'general'),
                        'product_url': product.get('metadata', {}).get('product_url', '')
                    }
                })
        
        return raw_texts
    
    def _apply_advanced_preprocessing(self, raw_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply advanced preprocessing using the imported functionality"""
        try:
            # Convert to format expected by AdvancedPreprocessor
            preprocessor_input = []
            for item in raw_texts:
                preprocessor_input.append({
                    'text': item['text'],
                    'source': item['source'],
                    'metadata': {
                        'source_id': item['source_id'],
                        'data_type': item['data_type'],
                        'original_rating': item.get('original_rating'),
                    }
                })
            
            # Apply preprocessing
            processed_result = self.preprocessor.process_dataset(preprocessor_input)
            
            logger.info("Advanced preprocessing completed")
            return processed_result
            
        except Exception as e:
            logger.error(f"Advanced preprocessing failed: {e}")
            # Fallback to basic preprocessing
            return self._basic_preprocessing(raw_texts)
    
    def _basic_preprocessing(self, raw_texts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback basic preprocessing if advanced preprocessing fails"""
        logger.info("Applying basic preprocessing fallback")
        
        processed_texts = []
        for item in raw_texts:
            text = item['text']
            
            # Basic text cleaning
            if len(text.strip()) >= self.config.min_text_length:
                cleaned_text = self._basic_text_cleaning(text)
                if cleaned_text:
                    processed_texts.append({
                        'text': cleaned_text,
                        'source': item['source'],
                        'metadata': item
                    })
        
        return {
            'processed_data': processed_texts,
            'stats': {
                'total_input': len(raw_texts),
                'total_output': len(processed_texts),
                'filtering_ratio': len(processed_texts) / len(raw_texts) if raw_texts else 0
            }
        }
    
    def _basic_text_cleaning(self, text: str) -> str:
        """Basic text cleaning"""
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove very short texts
        if len(text) < self.config.min_text_length:
            return ""
        
        # Truncate very long texts
        if len(text) > self.config.max_text_length:
            text = text[:self.config.max_text_length] + "..."
        
        return text
    
    def _convert_to_agent_format(self, scraped_data: Dict[str, Any], preprocessed_data: Dict[str, Any]) -> List[AgentReadyData]:
        """Convert preprocessed data to standardized agent format"""
        agent_ready_data = []
        
        processed_items = preprocessed_data.get('processed_data', [])
        
        for item in processed_items:
            try:
                # Extract metadata
                metadata = item.get('metadata', {})
                original_data = metadata.get('original_data', {})
                
                # Determine product category
                product_category = "general"
                if metadata.get('source') == 'tiki':
                    product_category = metadata.get('product_metadata', {}).get('product_category', 'general')
                elif scraped_data.get('keyword'):
                    # Infer category from keyword
                    keyword = scraped_data['keyword'].lower()
                    if any(tech_word in keyword for tech_word in ['phone', 'laptop', 'airpods', 'ipad', 'tablet']):
                        product_category = 'electronics'
                    elif any(fashion_word in keyword for fashion_word in ['dress', 'shirt', 'shoes', 'bag']):
                        product_category = 'fashion'
                
                # Create AgentReadyData instance
                agent_data = AgentReadyData(
                    text=item['text'],
                    source=item.get('source', 'unknown'),
                    data_type=metadata.get('data_type', 'unknown'),
                    metadata={
                        'source_id': metadata.get('source_id', 'unknown'),
                        'scraped_at': datetime.now().isoformat(),
                        'original_data': original_data,
                        'keyword': scraped_data.get('keyword', 'unknown')
                    },
                    original_rating=metadata.get('original_rating'),
                    language=self._detect_language(item['text']),
                    product_category=product_category
                )
                
                agent_ready_data.append(agent_data)
                
            except Exception as e:
                logger.error(f"Failed to convert item to agent format: {e}")
                continue
        
        return agent_ready_data
    
    def _detect_language(self, text: str) -> str:
        """Basic language detection"""
        # Count Vietnamese characters
        vietnamese_chars = "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
        vietnamese_count = sum(1 for char in text.lower() if char in vietnamese_chars)
        
        if vietnamese_count / len(text) > 0.02:  # 2% Vietnamese characters
            return "vietnamese"
        else:
            return "english"
    
    def _calculate_processing_stats(self, scraped_data: Dict[str, Any], agent_ready_data: List[AgentReadyData]) -> Dict[str, Any]:
        """Calculate processing statistics"""
        original_stats = scraped_data.get('scraping_stats', {})
        original_total = original_stats.get('total_data_points', 0)
        processed_total = len(agent_ready_data)
        
        # Count by source
        youtube_count = len([d for d in agent_ready_data if d.source == 'youtube'])
        tiki_count = len([d for d in agent_ready_data if d.source == 'tiki'])
        
        # Count by language
        vietnamese_count = len([d for d in agent_ready_data if d.language == 'vietnamese'])
        english_count = len([d for d in agent_ready_data if d.language == 'english'])
        
        return {
            'original_data_points': original_total,
            'processed_data_points': processed_total,
            'processing_retention_rate': processed_total / original_total if original_total > 0 else 0,
            'source_distribution': {
                'youtube': youtube_count,
                'tiki': tiki_count
            },
            'language_distribution': {
                'vietnamese': vietnamese_count,
                'english': english_count
            },
            'data_type_distribution': self._count_data_types(agent_ready_data)
        }
    
    def _count_data_types(self, agent_ready_data: List[AgentReadyData]) -> Dict[str, int]:
        """Count distribution of data types"""
        type_counts = {}
        for data in agent_ready_data:
            data_type = data.data_type
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        return type_counts

def preprocess_scraped_data(scraped_data: Dict[str, Any], config: Optional[PreprocessingConfig] = None) -> Dict[str, Any]:
    """
    Convenience function to preprocess scraped data
    
    Args:
        scraped_data: Output from UnifiedScraper
        config: Optional preprocessing configuration
        
    Returns:
        Processed data ready for sentiment agents
    """
    preprocessor = DataPreprocessor(config)
    return preprocessor.process_scraped_data(scraped_data)

if __name__ == "__main__":
    # Test the preprocessor with sample data
    sample_scraped_data = {
        'keyword': 'test keyword',
        'youtube_data': [{
            'video_id': 'test123',
            'comments': [
                {'text': 'This is a great product! I love it.', 'type': 'transcript_segment'},
                {'text': 'Not good quality, disappointed.', 'type': 'transcript_segment'}
            ]
        }],
        'tiki_data': [{
            'product_id': 'prod123',
            'product_name': 'Test Product',
            'product_category': 'electronics',
            'reviews': [
                {'text': 'Sản phẩm tốt, chất lượng ổn.', 'rating': 5, 'type': 'product_review'},
                {'text': 'Delivery was slow but product is ok.', 'rating': 3, 'type': 'product_review'}
            ]
        }],
        'scraping_stats': {'total_data_points': 4}
    }
    
    processed_data = preprocess_scraped_data(sample_scraped_data)
    print(f"Processed {len(processed_data['agent_ready_data'])} data points")
    print(f"Processing stats: {processed_data['processing_stats']}")
