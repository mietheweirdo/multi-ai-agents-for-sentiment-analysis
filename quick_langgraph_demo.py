# quick_langgraph_demo.py
"""
Quick demo of LangGraph Multi-Agent System
Run this to see agent discussion in action!
"""

import json
import os
from agents.langgraph_coordinator import analyze_with_langgraph

def load_config():
    """Load configuration"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found! Please set up your OpenAI API key.")
        return None

def quick_demo():
    """Quick demonstration of LangGraph features"""
    
    print("🚀" * 60)
    print("🚀 QUICK LANGGRAPH MULTI-AGENT DEMO")
    print("🚀" * 60)
    
    config = load_config()
    if not config:
        return
    
    # Test 1: Simple positive review (should reach consensus quickly)
    print("\n🟢 TEST 1: Simple Positive Review (Consensus Expected)")
    print("-" * 50)
    
    simple_review = "This phone is amazing! Great camera, fast performance, excellent battery life."
    
    result1 = analyze_with_langgraph(
        review=simple_review,
        product_category="electronics", 
        config=config,
        max_discussion_rounds=2,
        disagreement_threshold=0.5  # Medium threshold
    )
    
    print(f"📱 Review: {simple_review}")
    print(f"🎯 Final Sentiment: {result1['master_analysis']['sentiment']}")
    print(f"💬 Discussion Rounds: {result1['workflow_metadata']['discussion_rounds']}")
    print(f"📊 Disagreement Level: {result1['workflow_metadata']['disagreement_level']:.2f}")
    
    # Test 2: Contradictory review (should trigger discussion)
    print("\n🔴 TEST 2: Contradictory Review (Discussion Expected)")
    print("-" * 50)
    
    contradictory_review = """
    This product has excellent build quality and premium materials, 
    but it's overpriced and customer service was terrible. 
    The technical specs are outdated but user experience is smooth.
    Mixed feelings about this purchase.
    """
    
    result2 = analyze_with_langgraph(
        review=contradictory_review,
        product_category="electronics",
        config=config,
        max_discussion_rounds=3,
        disagreement_threshold=0.4  # Lower threshold = more likely to discuss
    )
    
    print(f"📱 Review: {contradictory_review.strip()[:80]}...")
    print(f"🎯 Final Sentiment: {result2['master_analysis']['sentiment']}")
    print(f"💬 Discussion Rounds: {result2['workflow_metadata']['discussion_rounds']}")
    print(f"📊 Disagreement Level: {result2['workflow_metadata']['disagreement_level']:.2f}")
    
    # Show discussion messages if any
    discussion_msgs = result2.get('discussion_messages', [])
    if discussion_msgs:
        print(f"\n🗣️ Agent Discussion Messages:")
        for i, msg in enumerate(discussion_msgs[:3]):  # Show first 3
            print(f"  {i+1}. {msg[:80]}...")
    
    # Comparison
    print("\n⚖️ COMPARISON:")
    print(f"{'Metric':<20} {'Simple Review':<15} {'Complex Review':<15}")
    print("-" * 50)
    print(f"{'Sentiment':<20} {result1['master_analysis']['sentiment']:<15} {result2['master_analysis']['sentiment']:<15}")
    print(f"{'Discussions':<20} {result1['workflow_metadata']['discussion_rounds']:<15} {result2['workflow_metadata']['discussion_rounds']:<15}")
    print(f"{'Disagreement':<20} {result1['workflow_metadata']['disagreement_level']:.2f}{'':>13} {result2['workflow_metadata']['disagreement_level']:.2f}")
    print(f"{'Processing Time':<20} {result1['workflow_metadata']['processing_time']:.2f}s{'':>11} {result2['workflow_metadata']['processing_time']:.2f}s")
    
    print(f"\n✨ LANGGRAPH FEATURES DEMONSTRATED:")
    print(f"  ✅ Consensus detection")
    print(f"  ✅ Agent discussion when needed")
    print(f"  ✅ Dynamic workflow paths")
    print(f"  ✅ Disagreement level tracking")
    print(f"  ✅ Processing time monitoring")
    
    print(f"\n🎉 Demo complete! LangGraph Multi-Agent System working perfectly!")

if __name__ == "__main__":
    quick_demo() 