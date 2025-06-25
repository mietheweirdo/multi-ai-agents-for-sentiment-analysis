# demo_enhanced_system.py
"""
Demo script for the enhanced multi-agent sentiment analysis system.
Shows the new FinRobot-like prompt organization and improved structure.
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
    """Demo basic sentiment analysis with the enhanced system"""
    print("=" * 60)
    print("ENHANCED MULTI-AGENT SENTIMENT ANALYSIS DEMO")
    print("=" * 60)
    
    # Load configuration
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
        
        # Initialize coordinator for this category
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category=category,
            agent_types=["quality", "experience", "user_experience", "business"],
            max_tokens_per_agent=600, #150 default
            max_rounds=2
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
    """Demo the new FinRobot-like prompt organization"""
    print("\n" + "=" * 60)
    print("PROMPT ORGANIZATION DEMO (FinRobot-like Structure)")
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

def main():
    """Main demo function"""
    print("🚀 STARTING ENHANCED MULTI-AGENT SENTIMENT ANALYSIS DEMO")
    print("This demo showcases the new FinRobot-like prompt organization")
    
    try:
        # Run all demos
        demo_prompt_organization()
        demo_basic_analysis()
        # demo_token_optimization()
        # demo_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nKey Improvements:")
        print("• Organized prompts in dedicated files (FinRobot-like structure)")
        print("• Better separation of concerns")
        print("• Improved maintainability and readability")
        print("• Product-category-specific prompt customization")
        print("• Token optimization with configurable limits")
        print("• Enhanced error handling and validation")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 