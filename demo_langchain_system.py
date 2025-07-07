#!/usr/bin/env python3
"""
Demo LangGraph Multi-Agent System
Input: Product keyword → Auto scrape YouTube + Tiki → LangGraph analysis → Business recommendations
"""

import json
import os

# Import existing functions
from agents.langgraph_coordinator import analyze_with_langgraph

# Import data pipeline
try:
    from data_pipeline import scrape_and_preprocess
    DATA_AVAILABLE = True
except ImportError:
    print("❌ Data pipeline not available. Please install dependencies.")
    DATA_AVAILABLE = False

def load_config():
    """Load config from existing file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def show_business_recommendations(result, index):
    """Display business recommendations nicely"""
    print(f"\n{'='*60}")
    print(f"📊 BUSINESS ANALYSIS #{index}")
    print(f"{'='*60}")
    
    # Review info
    review = result['review_text'][:100] + "..." if len(result['review_text']) > 100 else result['review_text']
    print(f"📝 Review: {review}")
    print(f"📦 Category: {result['product_category']}")
    
    # LangGraph specific info
    metadata = result.get('workflow_metadata', {})
    discussion_rounds = metadata.get('discussion_rounds', 0)
    consensus = metadata.get('consensus_reached', True)
    print(f"🔄 Discussion rounds: {discussion_rounds}")
    print(f"🤝 Consensus reached: {'Yes' if consensus else 'No'}")
    
    # Final sentiment
    master = result.get('master_analysis', {})
    final_sentiment = master.get('sentiment', 'unknown')
    confidence = master.get('confidence', 0.0)
    print(f"🎯 Final sentiment: {final_sentiment.upper()} ({confidence:.2f})")
    
    # Business recommendations (main focus)
    business = result.get('business_recommendations', {})
    if business:
        print(f"\n💼 BUSINESS RECOMMENDATIONS:")
        business_impact = business.get('business_impact', 'No recommendations')
        print(f"   {business_impact}")
        
        rec_confidence = business.get('confidence', 0.0)
        print(f"   Confidence: {rec_confidence:.2f}")
    
    processing_time = metadata.get('processing_time', 0.0)
    print(f"⏱️  Processing time: {processing_time:.2f}s")

def main():
    """Main demo function"""
    print("🚀" * 50)
    print("🚀 LANGGRAPH MULTI-AGENT DEMO")
    print("🚀" * 50)
    
    if not DATA_AVAILABLE:
        print("❌ Cannot run demo - data pipeline not available")
        return
    
    # Get keyword from user
    keyword = input("\n🔍 Enter product keyword to search for reviews: ").strip()
    if not keyword:
        print("❌ No keyword provided. Exiting.")
        return
    
    print(f"\n🔄 Scraping reviews for '{keyword}' from YouTube + Tiki...")
    
    try:
        # Auto scrape from both sources
        data = scrape_and_preprocess(
            keyword=keyword,
            sources=['youtube', 'tiki'],  # Auto both sources
            max_items_per_source=20  # Limit for demo
        )
        
        if not data:
            print("❌ No reviews found. Try a different keyword.")
            return
        
        print(f"✅ Found {len(data)} reviews")
        print(f"\n🤖 Running LangGraph multi-agent analysis...")
        
        # Load config
        config = load_config()
        
        # Analyze each review with LangGraph
        for i, item in enumerate(data, 1):
            try:
                result = analyze_with_langgraph(
                    review=item['review_text'],
                    product_category=item['product_category'],
                    config=config,
                    max_discussion_rounds=2,
                    disagreement_threshold=0.6
                )
                
                show_business_recommendations(result, i)
                
            except Exception as e:
                print(f"❌ Error analyzing review {i}: {e}")
        
        print(f"\n🎉 Demo completed! Analyzed {len(data)} reviews with LangGraph.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main() 