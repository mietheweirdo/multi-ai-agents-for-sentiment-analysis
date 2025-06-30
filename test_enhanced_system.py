#!/usr/bin/env python3
"""
Enhanced Multi-Agent Sentiment Analysis System - Comprehensive Test
Tests the enhanced coordinator with various configurations and scenarios
"""

import json
import os
from agents.enhanced_coordinator import EnhancedCoordinatorAgent
from agents.product_prompts import ProductPromptManager

print("TESTING: Enhanced Multi-Agent Sentiment Analysis System")
print("=" * 60)

def test_enhanced_system():
    """Test the enhanced multi-agent sentiment analysis system"""
    
    print("TESTING: Enhanced Multi-Agent Sentiment Analysis System")
    print("=" * 60)
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Sample reviews for different product categories
    sample_reviews = {
        "electronics": [
            "This smartphone is amazing! The battery life is incredible and the camera quality is outstanding. However, the delivery took longer than expected.",
            "The laptop is well-built and fast, but the customer service was terrible when I had an issue. The screen quality is excellent though.",
            "Great product quality and fast shipping. The user interface is intuitive and the performance exceeds expectations."
        ],
        "fashion": [
            "Beautiful dress with excellent fabric quality! The fit is perfect and the color is exactly as shown. Very happy with my purchase.",
            "The shoes are comfortable but the stitching started coming apart after a few weeks. Customer service was helpful with the return.",
            "Love the style and design! The material feels premium and the sizing was accurate. Will definitely buy more from this brand."
        ],
        "beauty_health": [
            "This skincare product is amazing! My skin feels so much better after just a week. The ingredients are high quality and it's worth every penny.",
            "The product didn't work as advertised and caused some irritation. The return process was easy though, so that's a plus.",
            "Excellent results and great customer service. The product is effective and the packaging is beautiful. Highly recommend!"
        ]
    }
    
    # Test different configurations
    test_configs = [
        {
            "name": "Electronics Analysis (4 agents, 150 tokens each)",
            "product_category": "electronics",
            "agent_types": ["quality", "experience", "user_experience", "business"],
            "max_tokens_per_agent": 150,
            "reviews": sample_reviews["electronics"]
        },
        {
            "name": "Fashion Analysis (3 agents, 100 tokens each)",
            "product_category": "fashion", 
            "agent_types": ["quality", "user_experience", "business"],
            "max_tokens_per_agent": 100,
            "reviews": sample_reviews["fashion"]
        },
        {
            "name": "Beauty Analysis (5 agents, 120 tokens each)",
            "product_category": "beauty_health",
            "agent_types": ["quality", "experience", "user_experience", "business", "technical"],
            "max_tokens_per_agent": 120,
            "reviews": sample_reviews["beauty_health"]
        }
    ]
    
    for test_config in test_configs:
        print(f"\n[ANALYSIS] {test_config['name']}")
        print("-" * 50)
        
        # Create coordinator with specific configuration
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category=test_config["product_category"],
            agent_types=test_config["agent_types"],
            max_tokens_per_agent=test_config["max_tokens_per_agent"]
        )
        
        # Run analysis
        try:
            result = coordinator.run_workflow(
                reviews=test_config["reviews"],
                product_category=test_config["product_category"]
            )
            
            # Display results
            print(f"\nAnalysis completed for {test_config['product_category']}")
            print(f"Total agents: {result['analysis_metadata']['total_agents']}")
            print(f"Processing time: {result['analysis_metadata']['processing_time']:.2f}s")
            print(f"Average confidence: {result['analysis_metadata']['average_confidence']:.2f}")
            print(f"Agent types: {', '.join(test_config['agent_types'])}")
            
            # Show consensus results
            consensus = result['consensus']
            print(f"Overall sentiment: {consensus.get('overall_sentiment', 'unknown')}")
            print(f"Overall confidence: {consensus.get('overall_confidence', 0.5):.2f}")
            print(f"Agreement level: {consensus.get('agreement_level', 'unknown')}")
            
            # Show key insights
            if 'key_insights' in consensus:
                print(f"\nKey insights:")
                insights = consensus['key_insights']
                if isinstance(insights, list):
                    for insight in insights[:3]:  # Top 3 insights
                        print(f"   - {insight}")
                else:
                    print(f"   - {insights}")
            
        except Exception as e:
            print(f"ERROR in {test_config['name']}: {e}")
    
    # Test category switching
    print(f"\nTesting Category Switching")
    print("-" * 30)
    
    coordinator = EnhancedCoordinatorAgent(config=config, product_category="electronics")
    print(f"Current category: {coordinator.product_category}")
    
    # Switch to fashion
    coordinator.change_product_category("fashion")
    print(f"Switched to: {coordinator.product_category}")
    
    # Show available categories
    print(f"\nAvailable product categories:")
    categories = coordinator.get_available_categories()
    for category in categories:
        description = ProductPromptManager.get_category_description(category)
        print(f"   - {category}: {description}")

def test_token_optimization():
    """Test different token configurations"""
    print(f"\nToken Optimization Test")
    print("-" * 40)
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    test_review = "This smartphone is amazing! The battery life is incredible and the camera quality is outstanding. However, the delivery took longer than expected."
    
    token_configs = [
        {
            "description": "Low token limit",
            "max_tokens": 50,
            "expected_trade_offs": "Fast but less detailed"
        },
        {
            "description": "Medium token limit", 
            "max_tokens": 150,
            "expected_trade_offs": "Balanced performance"
        },
        {
            "description": "High token limit",
            "max_tokens": 300,
            "expected_trade_offs": "Detailed but slower"
        }
    ]
    
    for token_config in token_configs:
        print(f"\nTesting {token_config['description']} configuration ({token_config['max_tokens']} tokens)")
        
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            agent_types=["quality", "experience"],
            max_tokens_per_agent=token_config['max_tokens']
        )
        
        try:
            result = coordinator.run_workflow(
                reviews=[test_review],
                product_category="electronics"
            )
            
            if result:
                processing_time = result['analysis_metadata']['processing_time']
                avg_confidence = result['analysis_metadata']['average_confidence']
                
                print(f"   Processing time: {processing_time:.2f}s")
                print(f"   Average confidence: {avg_confidence:.2f}")
                print(f"   Trade-offs: {token_config['expected_trade_offs']}")
                
        except Exception as e:
            print(f"   Error: {e}")

# Run all tests
if __name__ == "__main__":
    # Run main test
    test_enhanced_system()
    
    # Run token optimization test
    test_token_optimization()
    
    print(f"\nAll tests completed!")
    print("=" * 60) 