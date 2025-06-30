#!/usr/bin/env python3
"""
Quick Test for Evaluation System
Tests basic functionality before running full evaluation
"""

import json
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if required modules can be imported"""
    print("Testing imports...")
    
    try:
        from agents.enhanced_coordinator import EnhancedCoordinatorAgent
        print("   EnhancedCoordinatorAgent imported")
    except ImportError as e:
        print(f"   Error importing EnhancedCoordinatorAgent: {e}")
        return False
    
    try:
        from agents.sentiment_agents import SentimentAgentFactory
        print("   SentimentAgentFactory imported")
    except ImportError as e:
        print(f"   Error importing SentimentAgentFactory: {e}")
        return False
    
    try:
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        print("   sklearn metrics imported")
    except ImportError as e:
        print(f"   Error importing sklearn: {e}")
        print("   Run: pip install scikit-learn")
        return False
    
    try:
        import numpy as np
        print("   numpy imported")
    except ImportError as e:
        print(f"   Error importing numpy: {e}")
        return False
    
    return True

def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")
    
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"   Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'api_key' not in config:
            print("   API key not found in config")
            return False
        
        if not config['api_key'] or config['api_key'] == "your-openai-api-key-here":
            print("   Please set your OpenAI API key in config.json")
            return False
        
        print("   Configuration valid")
        return True
        
    except Exception as e:
        print(f"   Error reading config: {e}")
        return False

def test_dataset():
    """Test labeled dataset"""
    print("\nTesting labeled dataset...")
    
    dataset_path = "evaluation/labeled_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"   Dataset not found: {dataset_path}")
        return False
    
    try:
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        categories = list(dataset.keys())
        total_samples = sum(len(samples) for samples in dataset.values())
        
        print(f"   Dataset loaded: {len(categories)} categories, {total_samples} samples")
        
        for category, samples in dataset.items():
            print(f"     {category}: {len(samples)} samples")
        
        return True
        
    except Exception as e:
        print(f"   Error reading dataset: {e}")
        return False

def test_single_agent():
    """Test single agent functionality"""
    print("\nTesting single agent...")
    
    try:
        from agents.sentiment_agents import SentimentAgentFactory
        
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        # Load a sample from dataset
        with open("evaluation/labeled_dataset.json", 'r') as f:
            dataset = json.load(f)
        
        # Get first sample from electronics
        sample = dataset['electronics'][0]
        review = sample['review']
        ground_truth = sample['ground_truth']
        
        print(f"   Testing review: {review[:50]}...")
        print(f"   Ground truth: {ground_truth}")
        
        # Create agent
        agent = SentimentAgentFactory.create_agent(
            agent_type="user_experience",
            config=config,
            max_tokens=300,
            product_category="electronics"
        )
        
        # Analyze
        start_time = time.time()
        result = agent.analyze(review)
        analysis_time = time.time() - start_time
        
        predicted = result['sentiment']
        confidence = result['confidence']
        
        print(f"   Predicted: {predicted} (confidence: {confidence:.2f})")
        print(f"   Analysis time: {analysis_time:.2f}s")
        print(f"   {'Correct' if predicted == ground_truth else 'Incorrect'}")
        
        return True
        
    except Exception as e:
        print(f"   Error testing single agent: {e}")
        return False

def test_multi_agent():
    """Test multi-agent system"""
    print("\nTesting multi-agent system...")
    
    try:
        from agents.enhanced_coordinator import EnhancedCoordinatorAgent
        
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        # Load a sample from dataset
        with open("evaluation/labeled_dataset.json", 'r') as f:
            dataset = json.load(f)
        
        # Get first sample from electronics
        sample = dataset['electronics'][0]
        review = sample['review']
        ground_truth = sample['ground_truth']
        
        print(f"   Testing review: {review[:50]}...")
        print(f"   Ground truth: {ground_truth}")
        
        # Create coordinator
        coordinator = EnhancedCoordinatorAgent(
            config=config,
            product_category="electronics",
            agent_types=["quality", "experience", "user_experience"],
            max_tokens_per_agent=300
        )
        
        # Analyze
        start_time = time.time()
        result = coordinator.run_workflow(
            reviews=[review],
            product_category="electronics"
        )
        analysis_time = time.time() - start_time
        
        predicted = result['consensus']['overall_sentiment']
        confidence = result['consensus']['overall_confidence']
        
        print(f"   Predicted: {predicted} (confidence: {confidence:.2f})")
        agents_used = result['analysis_metadata']['total_agents']
        print(f"   Analysis time: {analysis_time:.2f}s")
        print(f"   {'Correct' if predicted == ground_truth else 'Incorrect'}")
        print(f"   Agents used: {agents_used}")
        
        return True
        
    except Exception as e:
        print(f"   Error testing multi-agent: {e}")
        return False

def main():
    """Run all quick tests"""
    print("QUICK EVALUATION SYSTEM TEST")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Dataset Test", test_dataset),
        ("Single Agent Test", test_single_agent),
        ("Multi-Agent Test", test_multi_agent)
    ]
    
    passed = 0
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            print(f"   {test_name}: PASSED")
            passed += 1
        else:
            print(f"   {test_name}: FAILED")
            break
    
    print(f"\nQuick Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("All quick tests passed! Ready for full evaluation.")
        return True
    else:
        print("Some tests failed. Please fix issues before running full evaluation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 