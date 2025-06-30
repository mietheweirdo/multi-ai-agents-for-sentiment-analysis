# test_langgraph_system.py
"""
Test script for LangGraph Multi-Agent Sentiment Analysis System
Demonstrates agent discussion, consensus building, and workflow visualization
"""

import json
import os
from agents.langgraph_coordinator import LangGraphCoordinator, analyze_with_langgraph

# Import the new data pipeline
try:
    from data_pipeline import scrape_and_preprocess
    DYNAMIC_DATA_AVAILABLE = True
except ImportError:
    print("Warning: Data pipeline not available. Using static data only.")
    DYNAMIC_DATA_AVAILABLE = False

def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def print_analysis_results(result, title="Analysis Results"):
    """Pretty print analysis results"""
    print(f"\n{'='*80}")
    print(f"📊 {title}")
    print(f"{'='*80}")
    
    # Basic info
    print(f"🔍 Review: {result['review_text'][:100]}...")
    print(f"📦 Product Category: {result['product_category']}")
    
    # Department analyses
    print(f"\n🏢 DEPARTMENT ANALYSES:")
    for i, analysis in enumerate(result.get('department_analyses', [])):
        agent_type = analysis.get('agent_type', 'unknown')
        sentiment = analysis.get('sentiment', 'unknown')
        confidence = analysis.get('confidence', 0.0)
        reasoning = analysis.get('reasoning', 'No reasoning')[:80]
        
        print(f"  {i+1}. {agent_type.upper()}: {sentiment} ({confidence:.2f})")
        print(f"     → {reasoning}...")
    
    # Discussion messages
    discussion_messages = result.get('discussion_messages', [])
    if discussion_messages:
        print(f"\n💬 AGENT DISCUSSION ({len(discussion_messages)} messages):")
        for i, message in enumerate(discussion_messages):
            print(f"  {i+1}. {message[:100]}...")
    else:
        print(f"\n💬 AGENT DISCUSSION: No discussion needed (consensus reached)")
    
    # Master analysis
    master = result.get('master_analysis', {})
    if master:
        print(f"\n🎯 MASTER ANALYSIS:")
        print(f"  Final Sentiment: {master.get('sentiment', 'unknown')} ({master.get('confidence', 0.0):.2f})")
        print(f"  Reasoning: {master.get('reasoning', 'No reasoning')[:100]}...")
    
    # Business recommendations
    business = result.get('business_recommendations', {})
    if business:
        print(f"\n💼 BUSINESS RECOMMENDATIONS:")
        business_impact = business.get('business_impact', 'No recommendations')
        print(f"  {business_impact[:150]}...")
    
    # Workflow metadata
    metadata = result.get('workflow_metadata', {})
    if metadata:
        print(f"\n⚙️ WORKFLOW METADATA:")
        print(f"  Processing Time: {metadata.get('processing_time', 0.0):.2f}s")
        print(f"  Discussion Rounds: {metadata.get('discussion_rounds', 0)}")
        print(f"  Disagreement Level: {metadata.get('disagreement_level', 0.0):.2f}")
        print(f"  Consensus Reached: {metadata.get('consensus_reached', True)}")
        print(f"  Total Departments: {metadata.get('total_departments', 0)}")

def test_consensus_case():
    """Test case where agents likely agree (no discussion needed)"""
    
    print("\n" + "🟢" * 50)
    print("🟢 TEST CASE 1: CONSENSUS EXPECTED (No Discussion)")
    print("🟢" * 50)
    
    # Clear positive review - agents should agree
    review = """
    This phone is absolutely fantastic! The camera quality is stunning, 
    battery life lasts all day, performance is lightning fast, 
    and the customer service was excellent when I had questions. 
    Delivery was quick and packaging was perfect. 
    Highly recommend this product to everyone!
    """
    
    config = load_config()
    
    # Use lower disagreement threshold so agents rarely discuss
    result = analyze_with_langgraph(
        review=review,
        product_category="electronics",
        config=config,
        max_discussion_rounds=2,
        disagreement_threshold=0.4  # Lower threshold = less likely to discuss
    )
    
    print_analysis_results(result, "CONSENSUS CASE - All Agents Agree")

def test_disagreement_case():
    """Test case where agents likely disagree (discussion needed)"""
    
    print("\n" + "🔴" * 50)
    print("🔴 TEST CASE 2: DISAGREEMENT EXPECTED (Discussion Needed)")
    print("🔴" * 50)
    
    # Mixed/contradictory review - agents should disagree and discuss
    review = """
    This product has amazing build quality and premium materials, 
    but it's way overpriced for what you get. The technical specs are outdated,
    customer service was rude and unhelpful, but the user experience is smooth.
    Shipping was fast but packaging was damaged. I'm conflicted about recommending this.
    Overall it's okay but has significant issues that are concerning.
    """
    
    config = load_config()
    
    # Use higher disagreement threshold so agents discuss more
    result = analyze_with_langgraph(
        review=review,
        product_category="electronics",
        config=config,
        max_discussion_rounds=3,
        disagreement_threshold=0.7  # Higher threshold = more likely to discuss
    )
    
    print_analysis_results(result, "DISAGREEMENT CASE - Agents Discuss & Refine")

def test_fashion_category():
    """Test with different product category"""
    
    print("\n" + "🟡" * 50)
    print("🟡 TEST CASE 3: FASHION CATEGORY SPECIALIZATION")
    print("🟡" * 50)
    
    review = """
    This dress is gorgeous and the fabric feels luxurious, 
    but the sizing runs small and the color faded after one wash.
    The style is trendy but the quality doesn't match the price point.
    Customer service was helpful with returns though.
    """
    
    config = load_config()
    
    result = analyze_with_langgraph(
        review=review,
        product_category="fashion",  # Different category
        config=config,
        max_discussion_rounds=2,
        disagreement_threshold=0.6
    )
    
    print_analysis_results(result, "FASHION CATEGORY - Specialized Prompts")

def test_custom_agents():
    """Test with custom set of agents"""
    
    print("\n" + "🟣" * 50)
    print("🟣 TEST CASE 4: CUSTOM AGENT SELECTION")
    print("🟣" * 50)
    
    review = """
    Great product with excellent technical specifications and build quality.
    Customer service could be better but overall satisfied with purchase.
    """
    
    config = load_config()
    
    # Use only specific agents
    custom_agents = ["quality", "technical", "business"]
    
    coordinator = LangGraphCoordinator(
        config=config,
        product_category="electronics",
        department_types=custom_agents,  # Custom agent selection
        max_discussion_rounds=2,
        disagreement_threshold=0.5
    )
    
    result = coordinator.run_analysis(review)
    
    print_analysis_results(result, "CUSTOM AGENTS - Quality, Technical, Business Only")

def compare_workflows():
    """Compare LangGraph vs Manual workflow"""
    
    print("\n" + "⚖️" * 50)
    print("⚖️ WORKFLOW COMPARISON: LangGraph vs Manual")
    print("⚖️" * 50)
    
    review = """
    This smartphone has excellent performance and camera quality,
    but battery life is disappointing and customer service was slow.
    Mixed feelings about this purchase.
    """
    
    config = load_config()
    
    # Test LangGraph workflow
    print("\n🔄 RUNNING LANGGRAPH WORKFLOW...")
    langgraph_result = analyze_with_langgraph(
        review=review,
        product_category="electronics",
        config=config,
        max_discussion_rounds=2,
        disagreement_threshold=0.6
    )
    
    # Test Manual workflow
    print("\n🔧 RUNNING MANUAL WORKFLOW...")
    from workflow_manager import analyze_review
    manual_result = analyze_review(
        review=review,
        product_category="electronics",
        config=config
    )
    
    # Print comparison
    print(f"\n📊 COMPARISON RESULTS:")
    print(f"{'Metric':<25} {'LangGraph':<15} {'Manual':<15}")
    print(f"{'-'*60}")
    
    lg_time = langgraph_result.get('workflow_metadata', {}).get('processing_time', 0)
    manual_time = manual_result.get('workflow_metadata', {}).get('processing_time', 0)
    print(f"{'Processing Time':<25} {lg_time:.2f}s{'':<9} {manual_time:.2f}s")
    
    lg_rounds = langgraph_result.get('workflow_metadata', {}).get('discussion_rounds', 0)
    print(f"{'Discussion Rounds':<25} {lg_rounds:<15} {'0 (N/A)':<15}")
    
    lg_consensus = langgraph_result.get('workflow_metadata', {}).get('consensus_reached', True)
    print(f"{'Consensus Reached':<25} {str(lg_consensus):<15} {'N/A':<15}")
    
    lg_sentiment = langgraph_result.get('master_analysis', {}).get('sentiment', 'unknown')
    manual_sentiment = manual_result.get('master_analysis', {}).get('sentiment', 'unknown')
    print(f"{'Final Sentiment':<25} {lg_sentiment:<15} {manual_sentiment:<15}")
    
    # Show unique features
    print(f"\n✨ UNIQUE LANGGRAPH FEATURES:")
    discussion_msgs = langgraph_result.get('discussion_messages', [])
    if discussion_msgs:
        print(f"  • Agent Discussion: {len(discussion_msgs)} discussion messages")
        print(f"  • Consensus Building: Disagreement level tracked")
        print(f"  • Iterative Refinement: Agents refined their analyses")
    else:
        print(f"  • Consensus Detection: No discussion needed (agents agreed)")
    
    print(f"\n🎯 MANUAL WORKFLOW ADVANTAGES:")
    print(f"  • Simplicity: Straightforward linear workflow")
    print(f"  • Speed: {manual_time:.2f}s vs {lg_time:.2f}s")
    print(f"  • Cost Efficiency: No discussion rounds = fewer API calls")

def test_with_dynamic_data():
    """Test LangGraph system with real scraped data"""
    
    if not DYNAMIC_DATA_AVAILABLE:
        print("❌ Dynamic data not available. Please install data pipeline dependencies.")
        return
    
    print("\n" + "🌐" * 50)
    print("🌐 DYNAMIC DATA TEST - Real Scraped Reviews")
    print("🌐" * 50)
    
    keyword = "smartphone"
    sources = ['tiki']  # Use Tiki only for reliability
    
    print(f"🔄 Scraping data for '{keyword}' from {sources}...")
    
    try:
        # Scrape real data
        data = scrape_and_preprocess(
            keyword=keyword,
            sources=sources,
            max_items_per_source=3  # Limit for test speed
        )
        
        if not data:
            print("❌ No data found for testing.")
            return
        
        print(f"✅ Found {len(data)} reviews. Testing with LangGraph...")
        
        config = load_config()
        
        # Test with first real review
        item = data[0]
        result = analyze_with_langgraph(
            review=item['review_text'],
            product_category=item['product_category'],
            config=config,
            max_discussion_rounds=2,
            disagreement_threshold=0.6
        )
        
        print_analysis_results(result, f"DYNAMIC DATA TEST - {keyword.upper()}")
        
    except Exception as e:
        print(f"❌ Dynamic data test failed: {e}")

def test_interactive_dynamic():
    """Interactive test with user-specified keywords"""
    
    if not DYNAMIC_DATA_AVAILABLE:
        print("❌ Dynamic data not available. Please install data pipeline dependencies.")
        return
    
    print("\n" + "🎮" * 50)
    print("🎮 INTERACTIVE DYNAMIC TEST")
    print("🎮" * 50)
    
    keyword = input("Enter search keyword: ").strip()
    if not keyword:
        keyword = "laptop"
    
    sources_input = input("Enter sources (youtube,tiki) or press Enter for tiki: ").strip()
    if not sources_input:
        sources = ['tiki']
    else:
        sources = [s.strip() for s in sources_input.split(',') if s.strip() in ['youtube', 'tiki']]
    
    print(f"\n🔄 Scraping '{keyword}' from {sources}...")
    
    try:
        data = scrape_and_preprocess(
            keyword=keyword,
            sources=sources,
            max_items_per_source=5
        )
        
        if not data:
            print("❌ No data found. Try a different keyword.")
            return
        
        print(f"✅ Found {len(data)} reviews. Select one to analyze:")
        
        # Show review options
        for i, item in enumerate(data[:5], 1):
            review_preview = item['review_text'][:60] + "..." if len(item['review_text']) > 60 else item['review_text']
            print(f"{i}. [{item.get('metadata', {}).get('source', 'unknown')}] {review_preview}")
        
        choice = input(f"\nSelect review (1-{min(5, len(data))}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(data):
                selected_item = data[choice_idx]
                
                config = load_config()
                result = analyze_with_langgraph(
                    review=selected_item['review_text'],
                    product_category=selected_item['product_category'],
                    config=config,
                    max_discussion_rounds=3,
                    disagreement_threshold=0.6
                )
                
                print_analysis_results(result, f"INTERACTIVE ANALYSIS - {keyword.upper()}")
            else:
                print("❌ Invalid selection.")
        except ValueError:
            print("❌ Please enter a valid number.")
            
    except Exception as e:
        print(f"❌ Interactive test failed: {e}")

def main():
    """Run all test cases"""
    
    print("🚀" * 80)
    print("🚀 LANGGRAPH MULTI-AGENT SENTIMENT ANALYSIS SYSTEM DEMO")
    print("🚀" * 80)
    
    # Interactive menu
    while True:
        print(f"\n📋 TEST OPTIONS:")
        print("1. Static data tests (fast, no scraping)")
        print("2. Dynamic data tests (requires internet)")
        print("3. Interactive dynamic analysis")
        print("4. All tests (static + dynamic)")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        try:
            if choice == "1":
                run_static_tests()
            elif choice == "2":
                test_with_dynamic_data()
            elif choice == "3":
                test_interactive_dynamic()
            elif choice == "4":
                run_static_tests()
                if DYNAMIC_DATA_AVAILABLE:
                    test_with_dynamic_data()
                else:
                    print("⚠️ Skipping dynamic tests - data pipeline not available")
            elif choice == "5":
                print("👋 Testing completed!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            
def run_static_tests():
    """Run all static tests"""
    test_consensus_case()
    test_disagreement_case()
    test_fashion_category()
    test_custom_agents()
    compare_workflows()

if __name__ == "__main__":
    main()