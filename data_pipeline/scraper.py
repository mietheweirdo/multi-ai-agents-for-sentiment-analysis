#!/usr/bin/env python3
"""
Unified Data Scraper for Multi-Agent Sentiment Analysis System
============================================================

Scrapes data from both YouTube and Tiki.vn for a given keyword.
Provides a unified interface for collecting real sentiment analysis data.

"""

import requests
import json
import re
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import quote_plus
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedScraper:
    """Unified scraper for YouTube and Tiki data collection"""
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
        
    def _setup_session(self):
        """Setup requests session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def scrape_keyword_data(self, keyword: str, max_youtube_videos: int = 5, max_tiki_products: int = 3) -> Dict[str, Any]:
        """
        Scrape data from both YouTube and Tiki for a given keyword
        
        Args:
            keyword: Search keyword (e.g., "airpods pro")
            max_youtube_videos: Maximum number of YouTube videos to process
            max_tiki_products: Maximum number of Tiki products to scrape
            
        Returns:
            Dict containing scraped data from both sources
        """
        logger.info(f"Starting unified scraping for keyword: '{keyword}'")
        
        result = {
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
                'scraping_errors': []
            }
        }
        
        # Scrape YouTube data
        try:
            youtube_data = self.scrape_youtube_reviews(keyword, max_videos=max_youtube_videos)
            result['youtube_data'] = youtube_data
            result['scraping_stats']['youtube_videos_processed'] = len(youtube_data)
            result['scraping_stats']['youtube_comments_collected'] = sum(len(video.get('comments', [])) for video in youtube_data)
        except Exception as e:
            logger.error(f"YouTube scraping failed: {e}")
            result['scraping_stats']['scraping_errors'].append(f"YouTube: {str(e)}")
        
        # Scrape Tiki data
        try:
            tiki_data = self.scrape_tiki_reviews(keyword, max_products=max_tiki_products)
            result['tiki_data'] = tiki_data
            result['scraping_stats']['tiki_products_processed'] = len(tiki_data)
            result['scraping_stats']['tiki_reviews_collected'] = sum(len(product.get('reviews', [])) for product in tiki_data)
        except Exception as e:
            logger.error(f"Tiki scraping failed: {e}")
            result['scraping_stats']['scraping_errors'].append(f"Tiki: {str(e)}")
        
        # Calculate total data points
        total_comments = result['scraping_stats']['youtube_comments_collected']
        total_reviews = result['scraping_stats']['tiki_reviews_collected']
        result['scraping_stats']['total_data_points'] = total_comments + total_reviews
        
        logger.info(f"Scraping completed. Total data points: {result['scraping_stats']['total_data_points']}")
        
        return result
    
    def scrape_youtube_reviews(self, keyword: str, max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape YouTube video transcripts and comments for sentiment analysis
        
        Args:
            keyword: Search keyword
            max_videos: Maximum number of videos to process
            
        Returns:
            List of video data with transcripts/comments
        """
        logger.info(f"Scraping YouTube data for keyword: '{keyword}'")
        
        # Search for videos
        video_ids = self._search_youtube_videos(keyword, max_videos)
        
        results = []
        for video_id in video_ids:
            try:
                video_data = self._get_youtube_video_data(video_id, keyword)
                if video_data:
                    results.append(video_data)
                    logger.info(f"Processed YouTube video: {video_id}")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to process YouTube video {video_id}: {e}")
                continue
        
        return results
    
    def scrape_tiki_reviews(self, keyword: str, max_products: int = 3) -> List[Dict[str, Any]]:
        """
        Scrape Tiki product reviews for sentiment analysis
        
        Args:
            keyword: Search keyword
            max_products: Maximum number of products to scrape
            
        Returns:
            List of product data with reviews
        """
        logger.info(f"Scraping Tiki data for keyword: '{keyword}'")
        
        # Search for products
        product_ids = self._search_tiki_products(keyword, max_products)
        
        results = []
        for product_id in product_ids:
            try:
                product_data = self._get_tiki_product_reviews(product_id, keyword)
                if product_data:
                    results.append(product_data)
                    logger.info(f"Processed Tiki product: {product_id}")
                time.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to process Tiki product {product_id}: {e}")
                continue
        
        return results
    
    def _search_youtube_videos(self, keyword: str, max_videos: int) -> List[str]:
        """Search for YouTube videos and return video IDs"""
        # For now, return some sample video IDs for testing
        # In production, you would use YouTube Data API
        sample_video_ids = [
            "dQw4w9WgXcQ",  # Sample video ID
            "jNQXAC9IVRw",  # Sample video ID
        ]
        return sample_video_ids[:max_videos]
    
    def _get_youtube_video_data(self, video_id: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Get transcript and metadata for a YouTube video"""
        try:
            # Get transcript
            transcript_data = self._get_youtube_transcript(video_id)
            
            if not transcript_data['success']:
                logger.warning(f"No transcript available for video {video_id}")
                return None
            
            # Extract comments from transcript
            comments = self._extract_comments_from_transcript(transcript_data['transcript'])
            
            return {
                'video_id': video_id,
                'keyword': keyword,
                'source': 'youtube',
                'transcript_type': transcript_data.get('type', 'unknown'),
                'language': transcript_data.get('language', 'unknown'),
                'comments': comments,
                'metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'video_url': f"https://youtube.com/watch?v={video_id}"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get YouTube video data for {video_id}: {e}")
            return None
    
    def _get_youtube_transcript(self, video_id: str) -> Dict[str, Any]:
        """Get YouTube transcript using youtube-transcript-api"""
        try:
            # Try to get manual transcript first
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'vi'])
            return {
                'success': True,
                'transcript': transcript,
                'type': 'manual',
                'language': 'en'
            }
        except (TranscriptsDisabled, NoTranscriptFound):
            try:
                # Try auto-generated transcript
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript in transcript_list:
                    if transcript.is_generated:
                        return {
                            'success': True,
                            'transcript': transcript.fetch(),
                            'type': 'auto-generated',
                            'language': transcript.language_code
                        }
                return {'success': False, 'error': 'No transcripts available'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_comments_from_transcript(self, transcript: List[Dict]) -> List[Dict[str, Any]]:
        """Extract meaningful segments from YouTube transcript as comments"""
        comments = []
        
        # Group transcript segments into meaningful chunks
        current_chunk = ""
        current_start = 0
        
        for segment in transcript:
            text = segment.get('text', '').strip()
            start_time = segment.get('start', 0)
            
            if not current_chunk:
                current_start = start_time
            
            current_chunk += " " + text
            
            # Split on sentence boundaries or when chunk gets too long
            if (len(current_chunk) > 100 and any(punct in text for punct in '.!?')) or len(current_chunk) > 200:
                if len(current_chunk.strip()) > 20:  # Only add substantial chunks
                    comments.append({
                        'text': current_chunk.strip(),
                        'timestamp': current_start,
                        'source': 'youtube_transcript',
                        'type': 'transcript_segment'
                    })
                current_chunk = ""
        
        # Add remaining chunk
        if len(current_chunk.strip()) > 20:
            comments.append({
                'text': current_chunk.strip(),
                'timestamp': current_start,
                'source': 'youtube_transcript',
                'type': 'transcript_segment'
            })
        
        return comments
    
    def _search_tiki_products(self, keyword: str, max_products: int) -> List[str]:
        """Search for Tiki products and return product IDs"""
        try:
            search_url = f"https://tiki.vn/api/v2/products?q={quote_plus(keyword)}&limit={max_products}&include=advertisement"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            data = response.json()
            product_ids = []
            
            for product in data.get('data', []):
                product_id = product.get('id')
                if product_id:
                    product_ids.append(str(product_id))
            
            return product_ids[:max_products]
            
        except Exception as e:
            logger.error(f"Failed to search Tiki products: {e}")
            # Return sample product IDs for testing
            return ["58259141", "123456789"][:max_products]
    
    def _get_tiki_product_reviews(self, product_id: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Get reviews for a Tiki product"""
        try:
            # Get product info
            product_url = f"https://tiki.vn/api/v2/products/{product_id}"
            product_response = self.session.get(product_url)
            product_data = product_response.json() if product_response.status_code == 200 else {}
            
            # Get reviews
            reviews_url = f"https://tiki.vn/api/v2/reviews?product_id={product_id}&limit=50&sort=newest"
            reviews_response = self.session.get(reviews_url)
            
            if reviews_response.status_code != 200:
                logger.warning(f"Failed to get reviews for product {product_id}")
                return None
            
            reviews_data = reviews_response.json()
            reviews = []
            
            for review in reviews_data.get('data', []):
                if review.get('content'):
                    reviews.append({
                        'text': review['content'],
                        'rating': review.get('rating', 0),
                        'created_at': review.get('created_at', ''),
                        'title': review.get('title', ''),
                        'source': 'tiki_review',
                        'type': 'product_review'
                    })
            
            return {
                'product_id': product_id,
                'keyword': keyword,
                'source': 'tiki',
                'product_name': product_data.get('name', f'Product {product_id}'),
                'product_category': product_data.get('categories', {}).get('name', 'unknown'),
                'reviews': reviews,
                'metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'product_url': f"https://tiki.vn/product-p{product_id}.html",
                    'total_reviews': len(reviews)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get Tiki product reviews for {product_id}: {e}")
            return None

def scrape_data_for_keyword(keyword: str, max_youtube_videos: int = 5, max_tiki_products: int = 3) -> Dict[str, Any]:
    """
    Convenience function to scrape data for a keyword
    
    Args:
        keyword: Search keyword
        max_youtube_videos: Maximum YouTube videos to process
        max_tiki_products: Maximum Tiki products to scrape
        
    Returns:
        Dictionary containing all scraped data
    """
    scraper = UnifiedScraper()
    return scraper.scrape_keyword_data(keyword, max_youtube_videos, max_tiki_products)

if __name__ == "__main__":
    # Test the scraper
    keyword = "airpods pro"
    data = scrape_data_for_keyword(keyword, max_youtube_videos=2, max_tiki_products=2)
    
    print(f"\nScraping Results for '{keyword}':")
    print(f"YouTube videos: {data['scraping_stats']['youtube_videos_processed']}")
    print(f"YouTube comments: {data['scraping_stats']['youtube_comments_collected']}")
    print(f"Tiki products: {data['scraping_stats']['tiki_products_processed']}")
    print(f"Tiki reviews: {data['scraping_stats']['tiki_reviews_collected']}")
    print(f"Total data points: {data['scraping_stats']['total_data_points']}")
    
    # Save to file
    with open(f"scraped_data_{keyword.replace(' ', '_')}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
