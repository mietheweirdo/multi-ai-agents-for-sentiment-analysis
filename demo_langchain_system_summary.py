#!/usr/bin/env python3
"""
Demo LangGraph Multi-Agent System - SUMMARY VERSION
Input: Product keyword → Auto scrape → Combine all reviews → Single LangGraph analysis → Extended Business recommendations
"""

import json
import os

# Import existing functions
from agents.langgraph_coordinator import LangGraphCoordinator

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

def combine_reviews(data):
    """Combine all reviews into single analysis dataset"""
    combined_text = ""
    review_count = len(data)
    
    # Add summary header
    combined_text += f"DATASET SUMMARY: Analyzing {review_count} customer reviews for comprehensive insights.\n\n"
    
    # Add each review with clear separation
    for i, item in enumerate(data, 1):
        review = item['review_text']
        source = item.get('metadata', {}).get('source', 'unknown')
        combined_text += f"REVIEW {i} (Source: {source.upper()}):\n{review}\n\n"
    
    # Add analysis instruction
    combined_text += f"ANALYSIS INSTRUCTION: Please analyze all {review_count} customer reviews above as a comprehensive dataset to provide overall sentiment assessment and detailed business recommendations for the product/brand."
    
    return combined_text, review_count

def show_summary_analysis(result, review_count):
    """Display comprehensive summary analysis"""
    print(f"\n{'='*80}")
    print(f"📊 COMPREHENSIVE BUSINESS ANALYSIS SUMMARY")
    print(f"{'='*80}")
    
    # Dataset info
    print(f"📈 Dataset: {review_count} customer reviews analyzed")
    print(f"📦 Category: {result['product_category']}")
    
    # LangGraph process info
    metadata = result.get('workflow_metadata', {})
    discussion_rounds = metadata.get('discussion_rounds', 0)
    consensus = metadata.get('consensus_reached', True)
    disagreement_level = metadata.get('disagreement_level', 0.0)
    
    print(f"\n🔄 LangGraph Process:")
    print(f"   Discussion rounds: {discussion_rounds}")
    print(f"   Consensus reached: {'Yes' if consensus else 'No'}")
    print(f"   Disagreement level: {disagreement_level:.2f}")
    
    # Department summaries
    departments = result.get('department_analyses', [])
    if departments:
        print(f"\n🏢 Department Analysis Summary:")
        sentiment_counts = {}
        for dept in departments:
            agent_type = dept.get('agent_type', 'unknown')
            sentiment = dept.get('sentiment', 'unknown')
            confidence = dept.get('confidence', 0.0)
            
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            print(f"   {agent_type.upper()}: {sentiment.upper()} ({confidence:.2f})")
        
        print(f"\n📊 Sentiment Distribution: {dict(sentiment_counts)}")
    
    # Master analysis
    master = result.get('master_analysis', {})
    if master:
        final_sentiment = master.get('sentiment', 'unknown')
        confidence = master.get('confidence', 0.0)
        reasoning = master.get('reasoning', 'No reasoning')
        
        print(f"\n🎯 MASTER ANALYST FINAL ASSESSMENT:")
        print(f"   Final Sentiment: {final_sentiment.upper()} ({confidence:.2f})")
        print(f"   Reasoning: {reasoning}")
    
    # Business recommendations (main focus - extended display)
    business = result.get('business_recommendations', {})
    if business:
        print(f"\n💼 COMPREHENSIVE BUSINESS RECOMMENDATIONS:")
        print(f"{'='*60}")
        
        business_impact = business.get('business_impact', 'No recommendations')
        rec_confidence = business.get('confidence', 0.0)
        rec_reasoning = business.get('reasoning', 'No reasoning')
        
        print(f"📋 RECOMMENDATIONS:\n{business_impact}")
        print(f"\n🎯 REASONING:\n{rec_reasoning}")
        print(f"\n📊 Confidence: {rec_confidence:.2f}")
        
        # Additional business details if available
        emotions = business.get('emotions', [])
        topics = business.get('topics', [])
        
        if emotions:
            print(f"\n😊 Key Customer Emotions: {', '.join(emotions)}")
        if topics:
            print(f"📌 Focus Areas: {', '.join(topics)}")
    
    # Processing stats
    processing_time = metadata.get('processing_time', 0.0)
    print(f"\n⚙️ Processing Stats:")
    print(f"   Total processing time: {processing_time:.2f}s")
    print(f"   Average per review: {processing_time/review_count:.2f}s")
    print(f"   Total departments: {metadata.get('total_departments', 0)}")

def main():
    """Main demo function"""
    print("🚀" * 60)
    print("🚀 LANGGRAPH MULTI-AGENT SUMMARY DEMO")
    print("🚀" * 60)
    
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
        # Auto scrape from both sources (more data for summary)
        data = scrape_and_preprocess(
            keyword=keyword,
            sources=['youtube', 'tiki'],
            max_items_per_source=5  # Increased for comprehensive analysis
        )
        
        if not data:
            print("❌ No reviews found. Try a different keyword.")
            return
        
        print(f"✅ Found {len(data)} reviews")
        print(f"🔗 Combining all reviews into single dataset...")
        
        # Combine all reviews
        combined_reviews, review_count = combine_reviews(data)
        
        print(f"📝 Combined dataset: {len(combined_reviews)} characters")
        
        # Show combined reviews content
        print(f"\n{'='*60}")
        print(f"📄 COMBINED REVIEWS CONTENT:")
        print(f"{'='*60}")
        print(combined_reviews[:1500] + "..." if len(combined_reviews) > 1500 else combined_reviews)
        print(f"{'='*60}")
        
        print(f"\n🤖 Running LangGraph comprehensive analysis...")
        
        # Load config
        config = load_config()
        
        # Create custom coordinator with enhanced business advisor for comprehensive analysis
        coordinator = LangGraphCoordinator(
            config=config,
            product_category=data[0]['product_category'],  # Use first item's category
            max_discussion_rounds=2,
            disagreement_threshold=0.6,
            max_tokens_advisor=2000  # Significantly increased for comprehensive recommendations
        )
        
        # Override business advisor with comprehensive analysis focus
        from agents.sentiment_agents import BusinessAdvisorAgent
        
        # Create enhanced business advisor with custom behavior for comprehensive analysis
        class ComprehensiveBusinessAdvisor(BusinessAdvisorAgent):
            def provide_recommendations(self, master_analysis, department_results, review):
                """Enhanced recommendations for comprehensive dataset analysis"""
                
                # Prepare detailed context
                context = "COMPREHENSIVE DATASET ANALYSIS RESULTS:\n\n"
                
                # Master analyst results with more detail
                master_sentiment = master_analysis.get('sentiment', 'neutral')
                master_confidence = master_analysis.get('confidence', 0.5)
                master_reasoning = master_analysis.get('reasoning', 'No reasoning provided')
                
                context += f"MASTER ANALYST FINAL ASSESSMENT:\n"
                context += f"- Final Sentiment: {master_sentiment} (confidence: {master_confidence:.2f})\n"
                context += f"- Master Reasoning: {master_reasoning}\n\n"
                
                # Detailed department summaries
                context += "DETAILED DEPARTMENT INSIGHTS:\n"
                for result in department_results:
                    agent_type = result.get('agent_type', 'unknown')
                    sentiment = result.get('sentiment', 'neutral')
                    confidence = result.get('confidence', 0.5)
                    reasoning = result.get('reasoning', 'No reasoning')
                    
                    context += f"- {agent_type.upper()} DEPT: {sentiment} ({confidence:.2f})\n"
                    context += f"  Reasoning: {reasoning}\n"
                
                # Enhanced prompt for comprehensive recommendations
                context += f"""

DATASET CONTENT: {review}

TASK: As a Senior Business Advisor, provide COMPREHENSIVE, DETAILED business recommendations based on this multi-review dataset analysis. 

REQUIREMENTS:
1. Provide SPECIFIC, ACTIONABLE recommendations (not generic advice)
2. Address insights from ALL departments
3. Prioritize recommendations by impact (High/Medium/Low)
4. Include both quick wins and long-term strategies
5. Consider the comprehensive nature of this dataset
6. Provide detailed reasoning for each recommendation
7. Estimate potential business impact

RESPONSE FORMAT:
- sentiment: {master_sentiment}
- confidence: your confidence in recommendations (0.0-1.0)
- emotions: key customer emotions identified across dataset
- topics: priority areas needing attention
- reasoning: DETAILED explanation of why these recommendations work (200-300 words)
- business_impact: COMPREHENSIVE impact analysis and expected outcomes (300-500 words)

Focus on turning these customer insights into profitable, actionable business strategies."""
                
                return self.analyze(context)
        
        # Replace with enhanced advisor
        coordinator.business_advisor = ComprehensiveBusinessAdvisor(
            config=config,
            max_tokens=2000,
            product_category=data[0]['product_category']
        )
        
        # Single comprehensive analysis
        result = coordinator.run_analysis(combined_reviews)
        
        # Display comprehensive results
        show_summary_analysis(result, review_count)
        
        print(f"\n🎉 Comprehensive analysis completed!")
        print(f"📊 {review_count} reviews analyzed in single LangGraph workflow")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 