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
        
        # Product category mapping for filtering
        self.category_keywords = {
            'phone': ['điện thoại', 'smartphone', 'mobile', 'iphone', 'samsung', 'xiaomi', 'poco', 'realme', 'oppo', 'vivo', 'huawei'],
            'laptop': ['laptop', 'máy tính xách tay', 'macbook', 'dell', 'hp', 'asus', 'acer', 'lenovo'],
            'tablet': ['tablet', 'máy tính bảng', 'ipad'],
            'camera': ['máy ảnh', 'camera', 'canon', 'nikon', 'sony camera', 'fujifilm'],
            'headphone': ['tai nghe', 'headphone', 'earphone', 'airpods', 'earbud'],
            'watch': ['đồng hồ', 'watch', 'apple watch', 'samsung watch'],
            'tv': ['tivi', 'smart tv', 'television', 'tv'],
            'speaker': ['loa', 'speaker', 'bluetooth speaker']
        }
        
        # Category blacklist - products to exclude when searching for specific categories
        self.category_blacklist = {
            'phone': ['máy ảnh', 'camera', 'lens', 'ống kính', 'tripod', 'chân máy', 'phụ kiện máy ảnh', 'case máy ảnh', 'sạc camera', 'pin camera'],
            'camera': ['điện thoại', 'smartphone', 'mobile phone', 'case điện thoại', 'sạc điện thoại', 'tai nghe', 'headphone'],
            'laptop': ['điện thoại', 'smartphone', 'mobile phone', 'tablet', 'tai nghe'],
            'headphone': ['điện thoại', 'smartphone', 'camera', 'máy ảnh', 'laptop'],
            'watch': ['điện thoại', 'smartphone', 'camera', 'máy ảnh', 'laptop', 'tai nghe']
        }
    
    def _detect_intended_category(self, keyword: str) -> str:
        """Detect the intended product category from the search keyword"""
        keyword_lower = keyword.lower()
        
        for category, terms in self.category_keywords.items():
            for term in terms:
                if term.lower() in keyword_lower:
                    return category
        
        return 'general'
    
    def _enhance_keyword_for_category(self, keyword: str, category: str) -> str:
        """Enhance search keyword to be more specific for the detected category"""
        if category == 'phone':
            # For phone searches, add 'điện thoại' to be more specific
            if 'điện thoại' not in keyword.lower() and 'smartphone' not in keyword.lower():
                return f"{keyword} điện thoại"
        elif category == 'camera':
            if 'máy ảnh' not in keyword.lower() and 'camera' not in keyword.lower():
                return f"{keyword} máy ảnh"
        
        return keyword
    
    def _is_product_relevant(self, product: Dict[str, Any], intended_category: str) -> bool:
        """Check if a product is relevant to the intended category"""
        if intended_category == 'general':
            return True
        
        product_name = product.get('name', '').lower()
        
        # Check if product matches the intended category
        if intended_category in self.category_keywords:
            category_terms = self.category_keywords[intended_category]
            has_category_match = any(term.lower() in product_name for term in category_terms)
            
            # Check if product contains blacklisted terms for this category
            if intended_category in self.category_blacklist:
                blacklist_terms = self.category_blacklist[intended_category]
                has_blacklisted_terms = any(term.lower() in product_name for term in blacklist_terms)
                
                # Product is relevant if it matches category terms and doesn't have blacklisted terms
                return has_category_match and not has_blacklisted_terms
            
            return has_category_match
        
        return True
    
    def _calculate_relevance_score(self, product: Dict[str, Any], keyword: str, intended_category: str) -> float:
        """Calculate relevance score for a product based on keyword and category"""
        score = 0.0
        product_name = product.get('name', '').lower()
        keyword_lower = keyword.lower()
        
        # Exact keyword match bonus
        if keyword_lower in product_name:
            score += 3.0
        
        # Partial keyword match
        keyword_words = keyword_lower.split()
        for word in keyword_words:
            if len(word) > 2 and word in product_name:
                score += 1.0
        
        # Category relevance bonus
        if intended_category in self.category_keywords:
            category_terms = self.category_keywords[intended_category]
            for term in category_terms:
                if term.lower() in product_name:
                    score += 2.0
                    break
        
        # Review count and rating bonus (higher quality products)
        review_count = product.get('review_count', 0)
        rating = product.get('rating_average', 0)
        
        if review_count > 10:
            score += 0.5
        if review_count > 100:
            score += 0.5
        if rating >= 4.0:
            score += 0.5
        
        return score
    
    def search_products(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for products on Tiki by keyword with relevance filtering"""
        # Detect intended category and enhance keyword
        intended_category = self._detect_intended_category(keyword)
        enhanced_keyword = self._enhance_keyword_for_category(keyword, intended_category)
        
        logger.info(f"Searching Tiki - Original: '{keyword}', Enhanced: '{enhanced_keyword}', Category: '{intended_category}'")
        
        search_url = "https://tiki.vn/api/v2/products"
        params = {
            'limit': min(self.config.tiki_max_products * 3, 60),  # Get more results to filter
            'q': enhanced_keyword,
            'include': 'advertisement',
            'aggregations': '2',
        }
        
        try:
            response = self.session.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            all_products = []
            
            for item in data.get('data', []):
                product = {
                    'id': item['id'],
                    'name': item['name'],
                    'price': item.get('price'),
                    'rating_average': item.get('rating_average', 0),
                    'review_count': item.get('review_count', 0),
                    'url': f"https://tiki.vn/{item.get('url_path', '')}"
                }
                all_products.append(product)
            
            # Filter products for relevance
            relevant_products = []
            for product in all_products:
                if self._is_product_relevant(product, intended_category):
                    relevance_score = self._calculate_relevance_score(product, keyword, intended_category)
                    product['relevance_score'] = relevance_score
                    relevant_products.append(product)
            
            # Sort by relevance score (descending) and take top N
            relevant_products.sort(key=lambda x: x['relevance_score'], reverse=True)
            final_products = relevant_products[:self.config.tiki_max_products]
            
            # Remove relevance_score from final output
            for product in final_products:
                product.pop('relevance_score', None)
            
            logger.info(f"Found {len(final_products)} relevant products out of {len(all_products)} total for keyword: {keyword}")
            
            if len(final_products) < len(all_products):
                logger.info(f"Filtered out {len(all_products) - len(final_products)} irrelevant products")
            
            return final_products
            
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
