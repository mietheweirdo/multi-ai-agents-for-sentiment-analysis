# test_enhanced_system.py
import json
import os
from agents.enhanced_coordinator import EnhancedCoordinatorAgent
from agents.product_prompts import ProductPromptManager

def test_enhanced_system():
    """Test the enhanced multi-agent sentiment analysis system"""
    
    print("🚀 Testing Enhanced Multi-Agent Sentiment Analysis System")
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
        print(f"\n📊 {test_config['name']}")
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
            print(f"\n✅ Analysis completed for {test_config['product_category']}")
            print(f"📈 Total reviews analyzed: {result['metadata']['total_reviews']}")
            print(f"🤖 Agents used: {result['metadata']['agents_used']}")
            print(f"💾 Estimated tokens used: {result['metadata']['estimated_tokens_used']}")
            print(f"🎯 Agent types: {', '.join(result['metadata']['agent_types'])}")
            
            # Show sentiment distribution
            if 'sentiment_distribution' in result:
                print(f"📊 Sentiment distribution: {result['sentiment_distribution']}")
            
            # Show key insights
            if 'key_insights' in result:
                print(f"\n💡 Key insights:")
                for insight in result['key_insights'][:3]:  # Top 3 insights
                    print(f"   • {insight}")
            
        except Exception as e:
            print(f"❌ Error in {test_config['name']}: {e}")
    
    # Test category switching
    print(f"\n🔄 Testing Category Switching")
    print("-" * 30)
    
    coordinator = EnhancedCoordinatorAgent(config=config, product_category="electronics")
    print(f"Current category: {coordinator.product_category}")
    
    # Switch to fashion
    coordinator.change_product_category("fashion")
    print(f"Switched to: {coordinator.product_category}")
    
    # Show available categories
    print(f"\n📋 Available product categories:")
    categories = coordinator.get_available_categories()
    for category in categories:
        description = ProductPromptManager.get_category_description(category)
        print(f"   • {category}: {description}")

def test_token_optimization():
    """Test different token configurations for cost optimization"""
    
    print(f"\n💰 Token Optimization Test")
    print("=" * 40)
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    test_review = "This smartphone is amazing! The battery life is incredible and the camera quality is outstanding. However, the delivery took longer than expected."
    
    token_configs = [
        {"max_tokens": 50, "description": "Ultra-low cost"},
        {"max_tokens": 100, "description": "Low cost"},
        {"max_tokens": 150, "description": "Balanced"},
        {"max_tokens": 200, "description": "High quality"}
    ]
    
    for token_config in token_configs:
        print(f"\n🔧 Testing {token_config['description']} configuration ({token_config['max_tokens']} tokens)")
        
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            max_tokens_per_agent=token_config['max_tokens']
        )
        
        try:
            result = coordinator.run_workflow(reviews=[test_review])
            
            estimated_cost = (result['metadata']['estimated_tokens_used'] / 1000) * 0.00015  # Rough cost estimate
            print(f"   Estimated cost: ${estimated_cost:.4f}")
            print(f"   Sentiment: {result.get('sentiment', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    # Run main test
    test_enhanced_system()
    
    # Run token optimization test
    test_token_optimization()
    
    print(f"\n🎉 All tests completed!")
    print("=" * 60) 