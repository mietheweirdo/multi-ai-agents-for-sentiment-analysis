#!/usr/bin/env python3
"""
Data scrapers for YouTube and Tiki platforms
"""

import os
import re
import time
import logging
import requests
from typing import List, Dict, Any, Optional
from .config import ScrapingConfig


# YouTube Data API imports (optional - only needed for keyword search)

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    class HttpError(Exception):
        pass

logger = logging.getLogger(__name__)

class YouTubeScraper:
    """YouTube comment scraper (keyword search only)"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
    
    def _get_youtube_service(self):
        """Create YouTube API service instance"""
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError("YouTube Data API not available. Install with: pip install google-api-python-client")
        
        if not self.config.youtube_api_key:
            raise ValueError("YouTube API key not configured. Set youtube_api_key in ScrapingConfig.")
        
        return build('youtube', 'v3', developerKey=self.config.youtube_api_key)

    def _search_videos(self, keyword: str) -> List[Dict[str, Any]]:
        """Search YouTube videos and return top results"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.search().list(
                part="id,snippet",
                q=keyword,
                type="video",
                maxResults=self.config.youtube_max_videos,
                order="relevance"
            )
            response = request.execute()
            
            videos = []
            for item in response['items']:
                videos.append({
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt']
                })
            return videos
        except HttpError as e:
            logger.error(f"Error searching YouTube videos: {e}")
            return []

    def _get_video_comments(self, video_id: str, video_title: str) -> List[Dict[str, Any]]:
        """Fetch comments for a single video (robust, paginated, error-handled)"""
        comments = []
        next_page_token = None
        comment_count = 0
        max_comments = self.config.youtube_max_comments
        try:
            youtube = self._get_youtube_service()
            while comment_count < max_comments:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, max_comments - comment_count),
                    pageToken=next_page_token,
                    textFormat="plainText"
                )
                response = request.execute()
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    content = comment['textDisplay']
                    if content.strip():
                        comments.append({
                            'id': item['id'],
                            'content': content,
                            'author': comment.get('authorDisplayName', ''),
                            'published_at': comment.get('publishedAt', ''),
                            'like_count': comment.get('likeCount', 0),
                            'video_id': video_id,
                            'video_title': video_title,
                            'source': 'youtube',
                            'data_type': 'comment',
                            'created_at': comment.get('publishedAt', '')
                        })
                        comment_count += 1
                        if comment_count >= max_comments:
                            break
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                time.sleep(0.1)  # Rate limiting
        except HttpError as e:
            logger.error(f"Error getting comments for {video_id}: {e}")
        return comments
    
    def scrape_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Scrape YouTube comments by searching for videos with keyword"""
        logger.info(f"Scraping YouTube for keyword: '{keyword}'")
        
        # Search for videos
        videos = self._search_videos(keyword)
        
        all_comments = []
        for video in videos:
            logger.info(f"Getting comments for video: {video['title']}")
            comments = self._get_video_comments(video['video_id'], video['title'])
            all_comments.extend(comments)
            time.sleep(1)  # Rate limiting between videos
        
        logger.info(f"YouTube: Found {len(all_comments)} comments from {len(videos)} videos")
        return all_comments

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
    
    def search_products(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for products on Tiki by keyword"""
        search_url = "https://tiki.vn/api/v2/products"
        params = {
            'limit': self.config.tiki_max_products,
            'q': keyword,
            'include': 'advertisement',
            'aggregations': '2',
        }
        
        try:
            response = self.session.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for item in data.get('data', []):
                products.append({
                    'id': item['id'],
                    'name': item['name'],
                    'price': item.get('price'),
                    'rating_average': item.get('rating_average', 0),
                    'review_count': item.get('review_count', 0),
                    'url': f"https://tiki.vn/{item.get('url_path', '')}"
                })
            
            logger.info(f"Found {len(products)} products for keyword: {keyword}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching Tiki products: {e}")
            return []
    
    def get_product_reviews(self, product_id: str, product_name: str) -> List[Dict[str, Any]]:
        """Get reviews for a specific product"""
        max_reviews = self.config.tiki_max_reviews_per_product
        
        # First get product info to determine spid
        product_api = f'https://tiki.vn/api/v2/products/{product_id}'
        try:
            response = self.session.get(product_api, headers=self.headers)
            response.raise_for_status()
            product_data = response.json()
            spid = product_data.get('current_seller', {}).get('id')
        except Exception as e:
            logger.warning(f"Could not get seller ID for product {product_id}: {e}")
            spid = None
        
        # Get reviews
        reviews_url = 'https://tiki.vn/api/v2/reviews'
        params = {
            'limit': '20',
            'include': 'comments,contribute_info,attribute_vote_summary',
            'sort': 'score|desc,id|desc,stars|all',
            'page': '1',
            'product_id': product_id,
        }
        
        if spid:
            params['spid'] = spid
        
        reviews = []
        page = 1
        
        while len(reviews) < max_reviews:
            params['page'] = str(page)
            
            try:
                response = self.session.get(reviews_url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                page_reviews = data.get('data', [])
                if not page_reviews:
                    break
                
                for review in page_reviews:
                    if len(reviews) >= max_reviews:
                        break
                        
                    reviews.append({
                        'id': review['id'],
                        'content': review['content'],
                        'rating': review['rating'],
                        'customer_name': review.get('created_by', {}).get('name', 'Anonymous'),
                        'created_at': review['created_at'],
                        'product_id': product_id,
                        'product_name': product_name,
                        'source': 'tiki',
                        'data_type': 'product_review'
                    })
                
                logger.info(f"Fetched page {page} for product {product_id}: {len(page_reviews)} reviews")
                page += 1
                
                # Check if there are more pages
                if page > data.get('paging', {}).get('last_page', 1):
                    break
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching reviews page {page} for product {product_id}: {e}")
                break
        
        logger.info(f"Collected {len(reviews)} reviews for product {product_id}")
        return reviews
    
    def scrape_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Scrape Tiki reviews by searching for products with keyword"""
        logger.info(f"Scraping Tiki for keyword: '{keyword}'")
        
        # Search for products
        products = self.search_products(keyword)
        
        all_reviews = []
        for product in products:
            logger.info(f"Getting reviews for product: {product['name']}")
            reviews = self.get_product_reviews(product['id'], product['name'])
            all_reviews.extend(reviews)
        
        logger.info(f"Tiki: Found {len(all_reviews)} reviews from {len(products)} products")
        return all_reviews
