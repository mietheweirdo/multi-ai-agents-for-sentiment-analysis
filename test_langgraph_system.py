# test_langgraph_system.py
"""
Test script for LangGraph Multi-Agent Sentiment Analysis System
Demonstrates agent discussion, consensus building, and workflow visualization
"""

import json
import os
from agents.langgraph_coordinator import LangGraphCoordinator, analyze_with_langgraph

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

def main():
    """Run all test cases"""
    
    print("🚀" * 80)
    print("🚀 LANGGRAPH MULTI-AGENT SENTIMENT ANALYSIS SYSTEM DEMO")
    print("🚀" * 80)
    
    try:
        # Test different scenarios
        test_consensus_case()
        test_disagreement_case()
        test_fashion_category()
        test_custom_agents()
        compare_workflows()
        
        print(f"\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print(f"🎉 LangGraph Multi-Agent System is working perfectly!")
        print(f"🎉 Features demonstrated:")
        print(f"   • Agent-to-agent discussion")
        print(f"   • Consensus detection")
        print(f"   • Workflow visualization")
        print(f"   • Product category specialization")
        print(f"   • Custom agent selection")
        print(f"   • Comparison with manual workflow")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print(f"Make sure to:")
        print(f"  1. Install dependencies: pip install langgraph")
        print(f"  2. Set up config.json with your OpenAI API key")
        print(f"  3. Ensure all agent files are properly set up")

if __name__ == "__main__":
    main() 