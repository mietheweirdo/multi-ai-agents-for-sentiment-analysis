#!/usr/bin/env python3
"""
Simple Evaluation Script for Multi-Agent Sentiment Analysis
Compares Single Agent vs Multi-Agent performance with basic metrics
"""

import json
import os
import sys
import time
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.langgraph_coordinator import LangGraphCoordinator
from agents.sentiment_agents import SentimentAgentFactory

class SimpleEvaluator:
    """Simple sentiment analysis evaluator"""
    
    def __init__(self):
        """Initialize evaluator"""
        # Load config
        with open("config.json", 'r') as f:
            self.config = json.load(f)
        
        # Load optimized dataset (no mixed labels)
        with open("evaluation/optimized_dataset.json", 'r') as f:
            self.dataset = json.load(f)
    
    def evaluate_single_agent(self, category: str = "electronics") -> Dict[str, Any]:
        """Evaluate single agent performance"""
        print(f"\n=== Evaluating Single Agent ({category}) ===")
        
        # Create single agent
        agent = SentimentAgentFactory.create_agent(
            agent_type="user_experience",
            config=self.config,
            max_tokens=150,
            product_category=category
        )
        
        results = []
        correct = 0
        total = 0
        start_time = time.time()
        
        for sample in self.dataset[category]:
            review = sample['review']
            ground_truth = sample['ground_truth']
            
            try:
                # Analyze with single agent
                analysis = agent.analyze(review)
                predicted = analysis['sentiment']
                confidence = analysis['confidence']
                
                is_correct = ground_truth == predicted
                if is_correct:
                    correct += 1
                total += 1
                
                results.append({
                    'review': review[:100] + "..." if len(review) > 100 else review,
                    'ground_truth': ground_truth,
                    'predicted': predicted,
                    'confidence': confidence,
                    'correct': is_correct
                })
                
                status = "✓" if is_correct else "✗"
                test_case = sample.get('test_case', 'unknown')
                print(f"  {status} {ground_truth} -> {predicted} (conf: {confidence:.2f}) | {test_case}")
                
            except Exception as e:
                print(f"  Error: {e}")
                results.append({
                    'review': review[:100] + "..." if len(review) > 100 else review,
                    'ground_truth': ground_truth,
                    'predicted': 'error',
                    'confidence': 0.0,
                    'correct': False
                })
                total += 1
        
        processing_time = time.time() - start_time
        accuracy = correct / total if total > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'processing_time': processing_time,
            'results': results
        }
    
    def evaluate_multi_agent(self, category: str = "electronics") -> Dict[str, Any]:
        """Evaluate multi-agent performance"""
        print(f"\n=== Evaluating Multi-Agent ({category}) ===")
        
        # Create LangGraph coordinator
        coordinator = LangGraphCoordinator(
            config=self.config,
            product_category=category,
            department_types=["quality", "experience", "user_experience", "business"],
            max_tokens_per_department=150,
            max_discussion_rounds=1  # Keep simple for evaluation
        )
        
        results = []
        correct = 0
        total = 0
        start_time = time.time()
        
        for sample in self.dataset[category]:
            review = sample['review']
            ground_truth = sample['ground_truth']
            
            try:
                # Analyze with LangGraph multi-agent system
                analysis_result = coordinator.run_analysis(review)
                
                # Extract sentiment from master_analysis
                master_analysis = analysis_result.get('master_analysis', {})
                predicted = master_analysis.get('sentiment', 'neutral')
                confidence = master_analysis.get('confidence', 0.5)
                
                is_correct = ground_truth == predicted
                if is_correct:
                    correct += 1
                total += 1
                
                results.append({
                    'review': review[:100] + "..." if len(review) > 100 else review,
                    'ground_truth': ground_truth,
                    'predicted': predicted,
                    'confidence': confidence,
                    'correct': is_correct
                })
                
                status = "✓" if is_correct else "✗"
                test_case = sample.get('test_case', 'unknown')
                print(f"  {status} {ground_truth} -> {predicted} (conf: {confidence:.2f}) | {test_case}")
                
            except Exception as e:
                print(f"  Error: {e}")
                results.append({
                    'review': review[:100] + "..." if len(review) > 100 else review,
                    'ground_truth': ground_truth,
                    'predicted': 'error',
                    'confidence': 0.0,
                    'correct': False
                })
                total += 1
        
        processing_time = time.time() - start_time
        accuracy = correct / total if total > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'processing_time': processing_time,
            'results': results
        }
    
    def compare_approaches(self, category: str = "electronics") -> Dict[str, Any]:
        """Compare single vs multi-agent approaches"""
        print(f"\n🔍 Comparing Single vs Multi-Agent for {category.upper()}")
        print("=" * 60)
        
        # Run evaluations
        single_result = self.evaluate_single_agent(category)
        multi_result = self.evaluate_multi_agent(category)
        
        # Calculate improvements
        accuracy_improvement = multi_result['accuracy'] - single_result['accuracy']
        accuracy_improvement_percent = (accuracy_improvement / single_result['accuracy'] * 100) if single_result['accuracy'] > 0 else 0
        
        # Print summary
        print(f"\n📊 RESULTS SUMMARY")
        print("=" * 40)
        print(f"Single Agent:")
        print(f"  Accuracy: {single_result['accuracy']:.1%} ({single_result['correct']}/{single_result['total']})")
        print(f"  Time: {single_result['processing_time']:.1f}s")
        
        print(f"\nMulti-Agent:")
        print(f"  Accuracy: {multi_result['accuracy']:.1%} ({multi_result['correct']}/{multi_result['total']})")
        print(f"  Time: {multi_result['processing_time']:.1f}s")
        
        print(f"\nImprovement:")
        print(f"  Accuracy: {accuracy_improvement:+.1%} ({accuracy_improvement_percent:+.1f}%)")
        time_ratio = multi_result['processing_time'] / single_result['processing_time'] if single_result['processing_time'] > 0 else 1
        print(f"  Time Ratio: {time_ratio:.1f}x")
        
        return {
            'category': category,
            'single_agent': single_result,
            'multi_agent': multi_result,
            'improvement': {
                'accuracy_improvement': accuracy_improvement,
                'accuracy_improvement_percent': accuracy_improvement_percent,
                'time_ratio': time_ratio
            }
        }
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all categories"""
        print("🚀 Running Full Evaluation")
        print("=" * 60)
        
        results = {}
        categories = list(self.dataset.keys())
        
        for category in categories:
            results[category] = self.compare_approaches(category)
        
        # Overall summary
        print(f"\n🎯 OVERALL SUMMARY")
        print("=" * 40)
        
        total_single_correct = sum(results[cat]['single_agent']['correct'] for cat in categories)
        total_single_total = sum(results[cat]['single_agent']['total'] for cat in categories)
        total_multi_correct = sum(results[cat]['multi_agent']['correct'] for cat in categories)
        total_multi_total = sum(results[cat]['multi_agent']['total'] for cat in categories)
        
        overall_single_accuracy = total_single_correct / total_single_total if total_single_total > 0 else 0
        overall_multi_accuracy = total_multi_correct / total_multi_total if total_multi_total > 0 else 0
        overall_improvement = overall_multi_accuracy - overall_single_accuracy
        
        print(f"Overall Single Agent: {overall_single_accuracy:.1%} ({total_single_correct}/{total_single_total})")
        print(f"Overall Multi-Agent: {overall_multi_accuracy:.1%} ({total_multi_correct}/{total_multi_total})")
        print(f"Overall Improvement: {overall_improvement:+.1%}")
        
        # Save results
        results['overall'] = {
            'single_accuracy': overall_single_accuracy,
            'multi_accuracy': overall_multi_accuracy,
            'improvement': overall_improvement,
            'total_samples': total_single_total
        }
        
        with open('evaluation/simple_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to evaluation/simple_results.json")
        
        return results

def main():
    """Main function"""
    print("🤖 Simple Multi-Agent Sentiment Analysis Evaluation")
    print("=" * 60)
    
    try:
        evaluator = SimpleEvaluator()
        results = evaluator.run_full_evaluation()
        
        print("\n✅ Evaluation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 