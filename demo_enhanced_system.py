# demo_enhanced_system.py
"""
Demo script for the enhanced multi-agent sentiment analysis system.
Shows the new organized prompt structure and improved architecture.
"""

import json
import os
from agents.enhanced_coordinator import EnhancedCoordinatorAgent
from agents.prompts import AgentPrompts, ProductPrompts, BasePrompts

def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def demo_basic_analysis():
    """Demo basic enhanced multi-agent sentiment analysis"""
    print("\n" + "=" * 60)
    print("ENHANCED MULTI-AGENT SENTIMENT ANALYSIS DEMO")
    print("=" * 60)
    
    config = load_config()
    
    # Sample reviews for different product categories
    sample_reviews = {
        "electronics": [
            "This smartphone is absolutely amazing! The camera quality is outstanding and the battery life lasts all day. The user interface is intuitive and the build quality feels premium. However, the delivery took longer than expected and customer service was a bit slow to respond to my questions."
        ],
        "fashion": [
            "I love this dress! The fabric is soft and comfortable, and the fit is perfect. The color is exactly as shown in the pictures. The delivery was fast and the packaging was beautiful. I've received many compliments when wearing it. Great value for money!"
        ],
        "home_garden": [
            "This coffee maker is a disappointment. The build quality feels cheap and it broke after just 2 weeks of use. The customer service was helpful and offered a replacement, but the new one has the same issues. Not worth the money at all."
        ]
    }
    
    # Test each product category
    for category, reviews in sample_reviews.items():
        print(f"\n{'='*20} TESTING {category.upper()} CATEGORY {'='*20}")
        
        # Initialize coordinator for this category with enhanced configuration
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category=category,
            agent_types=["quality", "experience", "user_experience", "business"],
            max_tokens_per_agent=600, #150 default
            max_rounds=4,
            max_tokens_consensus=2400  # Enhanced consensus token limit for longer recommendations
        )
        
        # Analyze the review
        result = coordinator.run_workflow(
            reviews=reviews,
            product_category=category
        )
        
        # Display results
        print(f"\n📊 ANALYSIS RESULTS FOR {category.upper()}:")
        print(f"Review: {result['review_text'][:100]}...")
        
        print(f"\n🤖 AGENT ANALYSES:")
        for i, analysis in enumerate(result['agent_analyses'], 1):
            agent_type = analysis['agent_type']
            sentiment = analysis['sentiment']
            confidence = analysis['confidence']
            reasoning = analysis['reasoning']
            
            print(f"  {i}. {agent_type.upper()}: {sentiment} (confidence: {confidence:.2f})")
            print(f"     Reasoning: {reasoning}")
        
        print(f"\n🎯 CONSENSUS:")
        consensus = result['consensus']
        print(f"  Overall Sentiment: {consensus.get('overall_sentiment', 'unknown')}")
        print(f"  Confidence: {consensus.get('overall_confidence', 0.5):.2f}")
        print(f"  Agreement Level: {consensus.get('agreement_level', 'unknown')}")
        print(f"  Key Insights: {consensus.get('key_insights', 'No insights')}")
        print(f"  Business Recommendations: {consensus.get('business_recommendations', 'No recommendations')}")
        
        print(f"\n📈 METADATA:")
        metadata = result['analysis_metadata']
        print(f"  Total Agents: {metadata['total_agents']}")
        print(f"  Discussion Rounds: {metadata['discussion_rounds']}")
        print(f"  Average Confidence: {metadata['average_confidence']:.2f}")

def demo_prompt_organization():
    """Demo the new organized prompt structure"""
    print("\n" + "=" * 60)
    print("PROMPT ORGANIZATION DEMO")
    print("=" * 60)
    
    print("\n📁 PROMPT STRUCTURE:")
    print("agents/prompts/")
    print("├── __init__.py          # Module initialization")
    print("├── base_prompts.py      # Common templates and utilities")
    print("├── agent_prompts.py     # Agent-specific prompts")
    print("├── product_prompts.py   # Product-category customizations")
    print("└── coordinator_prompts.py # Consensus and discussion prompts")
    
    print("\n🔧 AVAILABLE AGENT TYPES:")
    agent_types = AgentPrompts.get_available_agent_types()
    for agent_type in agent_types:
        description = AgentPrompts.get_agent_description(agent_type)
        print(f"  • {agent_type}: {description}")
    
    print("\n🏷️  AVAILABLE PRODUCT CATEGORIES:")
    categories = ProductPrompts.get_available_categories()
    for category in categories:
        description = ProductPrompts.get_category_description(category)
        print(f"  • {category}: {description}")
    
    print("\n💡 PROMPT CUSTOMIZATION EXAMPLE:")
    print("Base Quality Agent Prompt:")
    base_prompt = AgentPrompts.get_agent_prompt("quality", 150)
    print(f"  Length: {len(base_prompt)} characters")
    
    print("\nCustomized for Electronics:")
    electronics_prompt = ProductPrompts.customize_agent_prompt(base_prompt, "electronics", "quality")
    print(f"  Length: {len(electronics_prompt)} characters")
    print(f"  Added electronics-specific focus areas")

def demo_token_optimization():
    """Demo token optimization features"""
    print("\n" + "=" * 60)
    print("TOKEN OPTIMIZATION DEMO")
    print("=" * 60)
    
    config = load_config()
    
    # Test different token limits
    token_limits = [100, 150, 200]
    
    sample_review = "This product exceeded my expectations! The quality is excellent and the customer service was outstanding. I would definitely recommend it to others."
    
    for max_tokens in token_limits:
        print(f"\n🔢 TESTING WITH {max_tokens} TOKENS PER AGENT:")
        
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            max_tokens_per_agent=max_tokens,
            max_rounds=1
        )
        
        result = coordinator.run_workflow(reviews=[sample_review])
        
        # Calculate estimated token usage
        total_agents = len(coordinator.sentiment_agents)
        estimated_tokens = total_agents * max_tokens
        
        print(f"  Total Agents: {total_agents}")
        print(f"  Estimated Token Usage: {estimated_tokens}")
        print(f"  Consensus: {result['consensus'].get('overall_sentiment', 'unknown')}")
        
        # Show reasoning length (proxy for token usage)
        for analysis in result['agent_analyses']:
            reasoning_length = len(analysis.get('reasoning', ''))
            print(f"  {analysis['agent_type']} reasoning length: {reasoning_length} chars")

def demo_error_handling():
    """Demo error handling and fallback mechanisms"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING DEMO")
    print("=" * 60)
    
    config = load_config()
    
    # Test with invalid product category
    print("\n🚫 TESTING INVALID PRODUCT CATEGORY:")
    try:
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="invalid_category",
            max_tokens_per_agent=150
        )
    except ValueError as e:
        print(f"  Error caught: {e}")
        print("  ✅ Proper error handling for invalid categories")
    
    # Test with invalid agent type
    print("\n🚫 TESTING INVALID AGENT TYPE:")
    try:
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            agent_types=["invalid_agent_type"],
            max_tokens_per_agent=150
        )
    except ValueError as e:
        print(f"  Error caught: {e}")
        print("  ✅ Proper error handling for invalid agent types")

def demo_enhanced_business_recommendations():
    """Demo enhanced business recommendations with different configurations"""
    print("\n" + "=" * 60)
    print("ENHANCED BUSINESS RECOMMENDATIONS DEMO")
    print("=" * 60)
    
    config = load_config()
    
    # Sample review for detailed analysis
    sample_review = "This laptop has excellent performance and build quality. The battery life is impressive and the keyboard feels great. However, the customer support was terrible when I had an issue, and the delivery took longer than expected. The price is reasonable for the features offered."
    
    # Test different consensus token configurations
    consensus_configs = [
        {
            "name": "Standard Configuration (300 tokens)",
            "max_tokens_consensus": 300,
            "description": "Default setting for cost optimization"
        },
        {
            "name": "Enhanced Configuration (800 tokens)", 
            "max_tokens_consensus": 800,
            "description": "Balanced approach for detailed recommendations"
        },
        {
            "name": "Premium Configuration (1200 tokens)",
            "max_tokens_consensus": 1200,
            "description": "Maximum detail for comprehensive business insights"
        }
    ]
    
    for config_setting in consensus_configs:
        print(f"\n🔧 TESTING: {config_setting['name']}")
        print(f"   Description: {config_setting['description']}")
        print(f"   Consensus Token Limit: {config_setting['max_tokens_consensus']}")
        
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            agent_types=["quality", "experience", "user_experience", "business"],
            max_tokens_per_agent=400,
            max_rounds=2,
            max_tokens_consensus=config_setting['max_tokens_consensus']
        )
        
        result = coordinator.run_workflow(reviews=[sample_review])
        
        consensus = result['consensus']
        business_rec = consensus.get('business_recommendations', 'No recommendations')
        
        # Handle both string and dictionary formats
        if isinstance(business_rec, dict):
            business_rec_str = str(business_rec)
        elif isinstance(business_rec, list):
            business_rec_str = ' '.join(str(item) for item in business_rec)
        else:
            business_rec_str = str(business_rec)
        
        print(f"\n📋 BUSINESS RECOMMENDATIONS:")
        print(f"   Length: {len(business_rec_str)} characters")
        print(f"   Word count: {len(business_rec_str.split())} words")
        print(f"   Content: {business_rec_str}")
        
        print(f"\n💰 ESTIMATED COST:")
        total_tokens = (len(coordinator.sentiment_agents) * 400) + config_setting['max_tokens_consensus']
        estimated_cost = (total_tokens / 1000) * 0.00015  # Approximate GPT-4o-mini cost
        print(f"   Total tokens: {total_tokens}")
        print(f"   Estimated cost: ${estimated_cost:.4f}")
        
        print("-" * 80)

def main():
    """Main demo function"""
    print("🚀 STARTING ENHANCED MULTI-AGENT SENTIMENT ANALYSIS DEMO")
    print("This demo showcases the new organized prompt structure")
    
    try:
        # Run all demos
        # demo_prompt_organization()
        demo_basic_analysis()
        # demo_enhanced_business_recommendations()
        # demo_token_optimization()
        # demo_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey Improvements:")
        print("• Organized prompts in dedicated files")
        print("• Better separation of concerns")
        print("• Improved maintainability and readability")
        print("• Product-category-specific prompt customization")
        print("• Token optimization with configurable limits")
        print("• Enhanced error handling and validation")
        print("• Configurable business recommendations length")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 