#!/usr/bin/env python3
"""
Main data pipeline orchestrator
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from .config import ScrapingConfig, PreprocessingConfig, load_config_from_file, create_scraping_config_from_dict
from .scrapers import YouTubeScraper, TikiScraper
from .preprocessor import AdvancedPreprocessor
from .utils import standardize_for_agents, save_data_to_file, detect_product_category, calculate_processing_stats

logger = logging.getLogger(__name__)

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
            try:
                youtube_data = self.youtube_scraper.scrape_by_keyword(keyword)
                all_data.extend(youtube_data)
            except Exception as e:
                logger.error(f"YouTube scraping failed: {e}")
        
        if 'tiki' in sources:
            try:
                tiki_data = self.tiki_scraper.scrape_by_keyword(keyword)
                all_data.extend(tiki_data)
            except Exception as e:
                logger.error(f"Tiki scraping failed: {e}")
        
        logger.info(f"Total scraped items: {len(all_data)}")
        return all_data
    
    def run_full_pipeline(self, keyword: str, sources: List[str] = None,
                         product_category: str = None) -> Dict[str, Any]:
        """
        Run the complete pipeline: scrape -> preprocess -> standardize for agents.
        
        Args:
            keyword: Search keyword (required)
            sources: Sources to use ['youtube', 'tiki']. Default: both
            product_category: Product category for agent context (auto-detected if None)
            
        Returns:
            Dict containing:
            - agent_ready_data: Data ready for sentiment analysis agents
            - raw_data: Original scraped data
            - preprocessing_stats: Statistics from preprocessing
        """
        logger.info(f"Starting integrated data pipeline for keyword: '{keyword}'")
        
        # Scrape data by keyword only
        raw_data = self.scrape_by_keyword(keyword, sources)
        
        if not raw_data:
            logger.warning("No data was scraped")
            return {
                'agent_ready_data': [],
                'raw_data': [],
                'preprocessing_stats': {},
                'files': {}
            }

        # Save raw data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_data_file = os.path.join(self.scraping_config.output_dir, f"raw_data_{timestamp}.json")
        save_data_to_file(raw_data, raw_data_file, "raw data")

        # Preprocess data
        if self.scraping_config.enable_preprocessing:
            logger.info("Starting preprocessing")
            preprocessing_result = self.preprocessor.process_data(raw_data)
            processed_data = preprocessing_result['processed_data']
            preprocessing_stats = preprocessing_result['stats']
            
            # Save processed data
            processed_data_file = os.path.join(self.preprocessing_config.output_dir, f"processed_data_{timestamp}.json")
            save_data_to_file(preprocessing_result, processed_data_file, "processed data")
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
            processed_data_file = None

        # Auto-detect product category if not provided
        if not product_category and processed_data:
            # Use first item for category detection
            first_item = processed_data[0]
            product_name = first_item.get('metadata', {}).get('product_name', '')
            content = first_item.get('content', '')
            product_category = detect_product_category(content, product_name)
            logger.info(f"Auto-detected product category: {product_category}")
        elif not product_category:
            product_category = "general"

        # Standardize for agents
        agent_ready_data = standardize_for_agents(processed_data, product_category)

        # Save agent-ready data
        agent_data_file = os.path.join(self.preprocessing_config.output_dir, f"agent_ready_data_{timestamp}.json")
        save_data_to_file(agent_ready_data, agent_data_file, "agent-ready data")

        # Calculate final stats
        final_stats = calculate_processing_stats(len(raw_data), len(processed_data), len(agent_ready_data))
        final_stats.update(preprocessing_stats)

        logger.info(f"Pipeline completed. Prepared {len(agent_ready_data)} items for sentiment analysis")

        return {
            'agent_ready_data': agent_ready_data,
            'raw_data': raw_data,
            'processed_data': processed_data,
            'preprocessing_stats': final_stats,
            'product_category': product_category,
            'files': {
                'raw_data': raw_data_file,
                'processed_data': processed_data_file,
                'agent_ready': agent_data_file
            }
        }

def scrape_and_preprocess(keyword: str, sources: List[str] = None,
                         product_category: str = None, max_items_per_source: int = None,
                         config: dict = None) -> List[Dict[str, Any]]:
    """
    Convenience function to quickly scrape and preprocess data for agents.
    
    Args:
        keyword: Search keyword (required)
        sources: Sources to scrape from ['youtube', 'tiki']. Default: both
        product_category: Product category (auto-detected if None)
        max_items_per_source: Maximum items per source (applies to both YouTube comments and Tiki reviews)
        config: Configuration dictionary (loaded from config.json if None)
        
    Returns:
        List of agent-ready data items
    """
    # Load configuration
    if config is None:
        config = load_config_from_file()
    
    # Create scraping config from loaded config
    scraping_config = create_scraping_config_from_dict(config)
    
    # Apply max_items_per_source if specified
    if max_items_per_source:
        scraping_config.youtube_max_comments = min(max_items_per_source, scraping_config.youtube_max_comments)
        scraping_config.tiki_max_reviews_per_product = min(max_items_per_source, scraping_config.tiki_max_reviews_per_product)
    
    # Create pipeline
    pipeline = IntegratedDataPipeline(scraping_config=scraping_config)
    
    # Run pipeline (keyword-only)
    result = pipeline.run_full_pipeline(
        keyword=keyword,
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
        sources=['tiki']  # Only Tiki for now since YouTube search needs API key
    )
    
    print(f"Pipeline result:")
    print(f"- Raw data items: {len(result['raw_data'])}")
    print(f"- Agent-ready items: {len(result['agent_ready_data'])}")
    print(f"- Product category: {result['product_category']}")
    print(f"- Preprocessing stats: {result['preprocessing_stats']}")
    
    if result['agent_ready_data']:
        print(f"\nFirst agent-ready item:")
        import json
        print(json.dumps(result['agent_ready_data'][0], ensure_ascii=False, indent=2))
