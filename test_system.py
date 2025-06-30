#!/usr/bin/env python3
"""
Multi-Agent Sentiment Analysis System Test
Basic testing of the system components
"""

import json
import os
import sys

# Add project root to path for importing
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_imports():
    """Test if all required modules can be imported"""
    try:
        from agents.enhanced_coordinator import EnhancedCoordinatorAgent
        from agents.sentiment_agents import SentimentAgentFactory
        print("All imports successful")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    config_path = os.path.join(project_root, 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'api_key' not in config or not config['api_key']:
            print("WARNING: OpenAI API key not configured (tests may fail)")
            return False
        
        print("Configuration loaded successfully")
        return True
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in config file: {e}")
        return False

def test_single_agent():
    """Test single agent functionality"""
    try:
        config_path = os.path.join(project_root, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        agent = SentimentAgentFactory.create_agent(
            agent_type="quality",
            config=config,
            max_tokens=100,
            product_category="electronics"
        )
        
        test_review = "This product is amazing! Great quality and fast delivery."
        result = agent.analyze(test_review)
        
        print(f"Single agent test successful: {result['sentiment']}")
        return True
        
    except Exception as e:
        print(f"Single agent test failed: {e}")
        return False

def test_multi_agent():
    """Test multi-agent coordinator"""
    try:
        config_path = os.path.join(project_root, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            agent_types=["quality", "experience"],
            max_tokens_per_agent=100
        )
        
        test_review = "This smartphone has excellent camera quality but poor battery life."
        result = coordinator.run_workflow(
            reviews=[test_review],
            product_category="electronics"
        )
        
        if result and 'consensus' in result:
            sentiment = result['consensus'].get('overall_sentiment', 'unknown')
            print(f"Multi-agent test successful: {sentiment}")
            return True
        else:
            print("Multi-agent test failed: No valid result")
            return False
            
    except Exception as e:
        print(f"Multi-agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Multi-Agent Sentiment Analysis System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Single Agent Test", test_single_agent),
        ("Multi-Agent Test", test_multi_agent)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            print(f"{test_name}: PASSED")
            passed += 1
        else:
            print(f"{test_name}: FAILED")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed. Please check the configuration and dependencies.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
