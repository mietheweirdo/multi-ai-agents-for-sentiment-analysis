#!/usr/bin/env python3
"""
Integrated Data Pipeline for Multi-Agent Sentiment Analysis
==========================================================

This module provides a unified scraper that can fetch data from both YouTube and Tiki,
process it through an advanced preprocessing pipeline, and output standardized data
for the sentiment analysis agents.

Features:
- YouTube transcript scraping with fallback to auto-generated subtitles
- Tiki product review scraping with pagination support
- Advanced preprocessing with quality filtering, deduplication, and normalization
- Standardized output schema for downstream sentiment analysis agents
- Error handling and logging
"""

import json
import os
import re
import requests
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration for scraping operations"""
    # YouTube settings
    youtube_languages: List[str] = None
    youtube_fallback_auto: bool = True
    
    # Tiki settings
    tiki_max_reviews_per_product: int = 50
    tiki_max_products: int = 3
    
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
    min_text_length: int = 5
    max_text_length: int = 1000
    min_word_count: int = 2
    max_repetition_ratio: float = 0.8
    
    # Language detection
    vietnamese_char_threshold: float = 0.05
    english_word_threshold: float = 0.3
    
    # Deduplication settings
    similarity_threshold: float = 0.85
    ngram_size: int = 3
    
    # Privacy settings
    enable_pii_redaction: bool = True
    
    # Output settings
    output_dir: str = "preprocessed_data"
    agent_ready_format: bool = True

class YouTubeScraper:
    """YouTube transcript scraper"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api.formatters import TextFormatter
            self.transcript_api = YouTubeTranscriptApi
            self.text_formatter = TextFormatter()
        except ImportError:
            logger.error("youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
            raise
    
    def extract_video_id(self, youtube_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
            r'youtube\.com/v/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        return None
    
    def search_youtube_videos(self, keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos by keyword.
        Note: This is a placeholder implementation. For production use,
        you would need YouTube Data API v3 credentials.
        """
        logger.warning("YouTube search not implemented - requires YouTube Data API v3 key")
        logger.info("Please provide specific YouTube URLs for now")
        return []
    
    def get_transcript(self, video_id: str) -> Dict[str, Any]:
        """Get transcript for a YouTube video"""
        try:
            # Try to get manual transcript first
            transcript = self.transcript_api.get_transcript(
                video_id, 
                languages=self.config.youtube_languages
            )
            transcript_type = "manual"
            
        except Exception as manual_error:
            if not self.config.youtube_fallback_auto:
                return {
                    'success': False,
                    'error': str(manual_error),
                    'type': 'none'
                }
                
            try:
                # Get list of available transcripts
                transcript_list = self.transcript_api.list_transcripts(video_id)
                
                # Find auto-generated transcript in preferred language
                transcript = None
                for lang in self.config.youtube_languages:
                    try:
                        transcript = transcript_list.find_generated_transcript([lang])
                        break
                    except:
                        continue
                
                # If not found, get first available auto-generated transcript
                if not transcript:
                    for t in transcript_list:
                        if t.is_generated:
                            transcript = t
                            break
                    
                if not transcript:
                    raise Exception("No auto-generated transcripts available")
                
                transcript = transcript.fetch()
                transcript_type = "auto-generated"
                
            except Exception as auto_error:
                return {
                    'success': False,
                    'error': str(auto_error),
                    'type': 'none'
                }

        # Convert transcript to text
        text_content = self.text_formatter.format_transcript(transcript)
        
        return {
            'success': True,
            'video_id': video_id,
            'transcript': transcript,
            'text_content': text_content,
            'type': transcript_type,
            'language': transcript[0].get('language', self.config.youtube_languages[0]) if transcript else ''
        }
    
    def scrape_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Scrape YouTube videos by keyword (placeholder)"""
        # This would require YouTube Data API v3 implementation
        logger.warning(f"YouTube keyword search for '{keyword}' not implemented")
        return []
    
    def scrape_by_urls(self, youtube_urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape YouTube videos by URLs"""
        results = []
        
        for url in youtube_urls:
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.warning(f"Could not extract video ID from URL: {url}")
                continue
            
            logger.info(f"Getting transcript for video: {video_id}")
            transcript_result = self.get_transcript(video_id)
            
            if transcript_result['success']:
                # Convert to standardized format
                text_segments = transcript_result['text_content'].split('\n')
                comments = []
                
                for i, segment in enumerate(text_segments):
                    if segment.strip():
                        comments.append({
                            'id': f"{video_id}_{i}",
                            'content': segment.strip(),
                            'source': 'youtube',
                            'video_id': video_id,
                            'url': url,
                            'timestamp': None,
                            'created_at': datetime.now().isoformat()
                        })
                
                results.extend(comments)
            else:
                logger.error(f"Failed to get transcript for {video_id}: {transcript_result['error']}")
        
        return results

class TikiScraper:
    """Tiki product review scraper"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.session = requests.Session()
        
        # Default headers for Tiki requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
        }
    
    def search_products(self, keyword: str, limit: int = None) -> List[Dict[str, Any]]:
        """Search for products on Tiki by keyword"""
        if limit is None:
            limit = self.config.tiki_max_products
        
        search_url = "https://tiki.vn/api/v2/products"
        params = {
            'limit': limit,
            'q': keyword,
            'include': 'advertisement',
            'aggregations': '2',
        }
        
        try:
            response = self.session.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('data', [])
            
            logger.info(f"Found {len(products)} products for keyword: {keyword}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def extract_product_id_from_url(self, product_url: str) -> Optional[str]:
        """Extract product ID from Tiki product URL"""
        match = re.search(r'-p(\d+)\.html', product_url)
        return match.group(1) if match else None
    
    def get_product_reviews(self, product_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get reviews for a specific product"""
        if limit is None:
            limit = self.config.tiki_max_reviews_per_product
        
        # First get product info to determine spid
        product_api = f'https://tiki.vn/api/v2/products/{product_id}'
        try:
            resp = self.session.get(product_api, headers=self.headers)
            resp.raise_for_status()
            product_data = resp.json()
            
            seller_id = product_data.get('current_seller', {}).get('id')
            spid = seller_id  # Use seller_id as spid fallback
            
        except Exception as e:
            logger.warning(f"Could not get product info for {product_id}: {e}")
            spid = None
        
        # Get reviews
        reviews_url = 'https://tiki.vn/api/v2/reviews'
        params = {
            'limit': '20',  # Per page limit
            'include': 'comments,contribute_info,attribute_vote_summary',
            'sort': 'score|desc,id|desc,stars|all',
            'page': '1',
            'product_id': product_id,
        }
        
        if spid:
            params['spid'] = spid
        
        reviews = []
        page = 1
        
        while len(reviews) < limit:
            params['page'] = page
            
            try:
                response = self.session.get(reviews_url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                page_reviews = data.get('data', [])
                
                if not page_reviews:
                    break
                
                for review in page_reviews:
                    if len(reviews) >= limit:
                        break
                    
                    content = review.get('content', '').strip()
                    if content:  # Only include reviews with content
                        standardized_review = {
                            'id': review.get('id'),
                            'content': content,
                            'source': 'tiki',
                            'product_id': product_id,
                            'rating': review.get('rating'),
                            'title': review.get('title'),
                            'customer_id': review.get('customer_id'),
                            'created_at': review.get('created_at'),
                            'thank_count': review.get('thank_count', 0)
                        }
                        
                        created_by = review.get('created_by', {})
                        if created_by:
                            standardized_review.update({
                                'customer_name': created_by.get('name'),
                                'purchased_at': created_by.get('purchased_at')
                            })
                        
                        reviews.append(standardized_review)
                
                logger.info(f"Fetched page {page} for product {product_id}: {len(page_reviews)} reviews")
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching reviews for product {product_id}, page {page}: {e}")
                break
        
        logger.info(f"Collected {len(reviews)} reviews for product {product_id}")
        return reviews
    
    def scrape_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Scrape Tiki reviews by searching for products with keyword"""
        # Search for products
        products = self.search_products(keyword)
        
        all_reviews = []
        for product in products[:self.config.tiki_max_products]:
            product_id = str(product.get('id', ''))
            if product_id:
                logger.info(f"Getting reviews for product: {product.get('name', product_id)}")
                reviews = self.get_product_reviews(product_id)
                all_reviews.extend(reviews)
        
        return all_reviews
    
    def scrape_by_urls(self, product_urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape Tiki reviews by product URLs"""
        all_reviews = []
        
        for url in product_urls:
            product_id = self.extract_product_id_from_url(url)
            if product_id:
                logger.info(f"Getting reviews for product URL: {url}")
                reviews = self.get_product_reviews(product_id)
                all_reviews.extend(reviews)
            else:
                logger.warning(f"Could not extract product ID from URL: {url}")
        
        return all_reviews

class AdvancedPreprocessor:
    """Advanced preprocessing pipeline for scraped data"""
    
    def __init__(self, config: PreprocessingConfig):
        self.config = config
        self.stats = {
            'total_loaded': 0,
            'filtered_quality': 0,
            'filtered_duplicates': 0,
            'processed_successfully': 0,
            'language_distribution': {},
            'source_distribution': {}
        }
        
        # Cache for duplicate detection
        self.seen_hashes: Set[str] = set()
        
    def _calculate_text_hash(self, text: str) -> str:
        """Calculate hash for duplicate detection"""
        # Normalize text for hashing
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_quality_text(self, text: str) -> bool:
        """Check if text meets quality requirements"""
        if not text or not text.strip():
            return False
        
        text = text.strip()
        
        # Length checks
        if len(text) < self.config.min_text_length or len(text) > self.config.max_text_length:
            return False
        
        # Word count check
        words = text.split()
        if len(words) < self.config.min_word_count:
            return False
        
        # Repetition check
        if len(words) > 1:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_count = max(word_counts.values())
            repetition_ratio = max_count / len(words)
            
            if repetition_ratio > self.config.max_repetition_ratio:
                return False
        
        return True
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for Vietnamese/English"""
        if not text:
            return 'unknown'
        
        # Vietnamese character patterns
        vietnamese_chars = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]'
        vietnamese_count = len(re.findall(vietnamese_chars, text, re.IGNORECASE))
        vietnamese_ratio = vietnamese_count / len(text) if text else 0
        
        if vietnamese_ratio >= self.config.vietnamese_char_threshold:
            return 'vietnamese'
        
        # English word detection
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)
        english_ratio = len(english_words) / len(text.split()) if text.split() else 0
        
        if english_ratio >= self.config.english_word_threshold:
            return 'english'
        
        return 'mixed'
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Basic text cleanup
        text = re.sub(r'https?://\S+', '[URL]', text)  # Replace URLs
        text = re.sub(r'\d{10,}', '[PHONE]', text)     # Replace phone numbers
        
        return text.strip()
    
    def process_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process scraped data through the preprocessing pipeline"""
        self.stats['total_loaded'] = len(raw_data)
        
        processed_items = []
        
        for item in raw_data:
            content = item.get('content', '')
            
            # Quality filtering
            if not self._is_quality_text(content):
                self.stats['filtered_quality'] += 1
                continue
            
            # Duplicate detection
            text_hash = self._calculate_text_hash(content)
            if text_hash in self.seen_hashes:
                self.stats['filtered_duplicates'] += 1
                continue
            self.seen_hashes.add(text_hash)
            
            # Text normalization
            normalized_content = self._normalize_text(content)
            
            # Language detection
            language = self._detect_language(normalized_content)
            
            # Create processed item
            processed_item = {
                'id': item.get('id', ''),
                'content': normalized_content,
                'original_content': content,
                'source': item.get('source', 'unknown'),
                'language': language,
                'created_at': item.get('created_at', ''),
                'metadata': {
                    'rating': item.get('rating'),
                    'product_id': item.get('product_id'),
                    'video_id': item.get('video_id'),
                    'url': item.get('url'),
                    'customer_name': item.get('customer_name'),
                    'thank_count': item.get('thank_count', 0)
                }
            }
            
            processed_items.append(processed_item)
            self.stats['processed_successfully'] += 1
            
            # Update stats
            source = item.get('source', 'unknown')
            self.stats['source_distribution'][source] = self.stats['source_distribution'].get(source, 0) + 1
            self.stats['language_distribution'][language] = self.stats['language_distribution'].get(language, 0) + 1
        
        return {
            'processed_data': processed_items,
            'stats': self.stats,
            'config': {
                'min_content_length': self.config.min_content_length,
                'max_content_length': self.config.max_content_length,
                'enable_deduplication': self.config.enable_deduplication,
                'similarity_threshold': self.config.similarity_threshold,
                'target_language': self.config.target_language
            }
        }

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
                'rating': item['metadata'].get('rating'),
                'product_id': item['metadata'].get('product_id'),
                'video_id': item['metadata'].get('video_id')
            }
        }
        
        standardized_items.append(standardized_item)
    
    return standardized_items

class IntegratedDataPipeline:
    """Main class that orchestrates scraping and preprocessing"""
    
    def __init__(self, scraping_config: ScrapingConfig = None, preprocessing_config: PreprocessingConfig = None):
        self.scraping_config = scraping_config or ScrapingConfig()
        self.preprocessing_config = preprocessing_config or PreprocessingConfig()
        
        self.youtube_scraper = YouTubeScraper(self.scraping_config)
        self.tiki_scraper = TikiScraper(self.scraping_config)
        self.preprocessor = AdvancedPreprocessor(self.preprocessing_config)
        
        # Create output directories
        os.makedirs(self.scraping_config.output_dir, exist_ok=True)
        os.makedirs(self.preprocessing_config.output_dir, exist_ok=True)
    
    def scrape_by_keyword(self, keyword: str, sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape data from multiple sources using a keyword.
        
        Args:
            keyword: Search keyword
            sources: List of sources to scrape from ['youtube', 'tiki']. Default: both
            
        Returns:
            List of raw scraped data
        """
        if sources is None:
            sources = ['youtube', 'tiki']
        
        all_data = []
        
        if 'youtube' in sources:
            logger.info(f"Scraping YouTube for keyword: {keyword}")
            youtube_data = self.youtube_scraper.scrape_by_keyword(keyword)
            all_data.extend(youtube_data)
            logger.info(f"YouTube: Found {len(youtube_data)} items")
        
        if 'tiki' in sources:
            logger.info(f"Scraping Tiki for keyword: {keyword}")
            tiki_data = self.tiki_scraper.scrape_by_keyword(keyword)
            all_data.extend(tiki_data)
            logger.info(f"Tiki: Found {len(tiki_data)} items")
        
        logger.info(f"Total scraped items: {len(all_data)}")
        return all_data
    
    def scrape_by_urls(self, youtube_urls: List[str] = None, tiki_urls: List[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape data from specific URLs.
        
        Args:
            youtube_urls: List of YouTube video URLs
            tiki_urls: List of Tiki product URLs
            
        Returns:
            List of raw scraped data
        """
        all_data = []
        
        if youtube_urls:
            logger.info(f"Scraping {len(youtube_urls)} YouTube URLs")
            youtube_data = self.youtube_scraper.scrape_by_urls(youtube_urls)
            all_data.extend(youtube_data)
            logger.info(f"YouTube: Found {len(youtube_data)} items")
        
        if tiki_urls:
            logger.info(f"Scraping {len(tiki_urls)} Tiki URLs")
            tiki_data = self.tiki_scraper.scrape_by_urls(tiki_urls)
            all_data.extend(tiki_data)
            logger.info(f"Tiki: Found {len(tiki_data)} items")
        
        logger.info(f"Total scraped items: {len(all_data)}")
        return all_data
    
    def run_full_pipeline(self, keyword: str = None, youtube_urls: List[str] = None, 
                         tiki_urls: List[str] = None, sources: List[str] = None,
                         product_category: str = "general") -> Dict[str, Any]:
        """
        Run the complete pipeline: scrape -> preprocess -> standardize for agents.
        
        Args:
            keyword: Search keyword (for scraping by keyword)
            youtube_urls: Specific YouTube URLs to scrape
            tiki_urls: Specific Tiki URLs to scrape
            sources: Sources to use when scraping by keyword
            product_category: Product category for agent context
            
        Returns:
            Dict containing:
            - agent_ready_data: Data ready for sentiment analysis agents
            - raw_data: Original scraped data
            - preprocessing_stats: Statistics from preprocessing
        """
        logger.info("Starting integrated data pipeline")
        
        # Scrape data
        if keyword:
            raw_data = self.scrape_by_keyword(keyword, sources)
        else:
            raw_data = self.scrape_by_urls(youtube_urls, tiki_urls)
        
        if not raw_data:
            logger.warning("No data was scraped")
            return {
                'agent_ready_data': [],
                'raw_data': [],
                'preprocessing_stats': {}
            }
        
        # Save raw data
        raw_data_file = os.path.join(self.scraping_config.output_dir, f"raw_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(raw_data_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Raw data saved to: {raw_data_file}")
        
        # Preprocess data
        if self.scraping_config.enable_preprocessing:
            logger.info("Starting preprocessing")
            preprocessing_result = self.preprocessor.process_data(raw_data)
            processed_data = preprocessing_result['processed_data']
            preprocessing_stats = preprocessing_result['stats']
            
            # Save processed data
            processed_data_file = os.path.join(self.preprocessing_config.output_dir, f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(processed_data_file, 'w', encoding='utf-8') as f:
                json.dump(preprocessing_result, f, ensure_ascii=False, indent=2)
            logger.info(f"Processed data saved to: {processed_data_file}")
        else:
            # Convert raw data to processed format
            processed_data = []
            for item in raw_data:
                processed_item = {
                    'id': item.get('id', ''),
                    'content': item.get('content', ''),
                    'source': item.get('source', 'unknown'),
                    'language': 'unknown',
                    'created_at': item.get('created_at', ''),
                    'metadata': item
                }
                processed_data.append(processed_item)
            
            preprocessing_stats = {'preprocessing_disabled': True}
        
        # Standardize for agents
        agent_ready_data = standardize_for_agents(processed_data, product_category)
        
        # Save agent-ready data
        agent_data_file = os.path.join(self.preprocessing_config.output_dir, f"agent_ready_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(agent_data_file, 'w', encoding='utf-8') as f:
            json.dump(agent_ready_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Agent-ready data saved to: {agent_data_file}")
        
        logger.info(f"Pipeline completed. Prepared {len(agent_ready_data)} items for sentiment analysis")
        
        return {
            'agent_ready_data': agent_ready_data,
            'raw_data': raw_data,
            'preprocessing_stats': preprocessing_stats,
            'files': {
                'raw_data': raw_data_file,
                'processed_data': processed_data_file if self.scraping_config.enable_preprocessing else None,
                'agent_ready': agent_data_file
            }
        }

# Convenience function for quick usage
def scrape_and_preprocess(keyword: str = None, youtube_urls: List[str] = None, 
                         tiki_urls: List[str] = None, product_category: str = "general",
                         sources: List[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to quickly scrape and preprocess data for agents.
    
    Args:
        keyword: Search keyword
        youtube_urls: YouTube video URLs
        tiki_urls: Tiki product URLs  
        product_category: Product category
        sources: Sources to scrape from
        
    Returns:
        List of agent-ready data items
    """
    pipeline = IntegratedDataPipeline()
    result = pipeline.run_full_pipeline(
        keyword=keyword,
        youtube_urls=youtube_urls,
        tiki_urls=tiki_urls,
        sources=sources,
        product_category=product_category
    )
    return result['agent_ready_data']

if __name__ == "__main__":
    # Example usage
    logger.info("Testing integrated data pipeline")
    
    # Test with keyword
    pipeline = IntegratedDataPipeline()
    
    # Example: scrape airpods reviews from Tiki
    result = pipeline.run_full_pipeline(
        keyword="airpods",
        sources=['tiki'],  # Only Tiki for now since YouTube search needs API key
        product_category="electronics"
    )
    
    print(f"Pipeline result:")
    print(f"- Raw data items: {len(result['raw_data'])}")
    print(f"- Agent-ready items: {len(result['agent_ready_data'])}")
    print(f"- Preprocessing stats: {result['preprocessing_stats']}")
    
    if result['agent_ready_data']:
        print(f"\nFirst agent-ready item:")
        print(json.dumps(result['agent_ready_data'][0], ensure_ascii=False, indent=2))
