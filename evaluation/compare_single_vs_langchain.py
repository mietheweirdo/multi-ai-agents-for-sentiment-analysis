#!/usr/bin/env python3
"""
Single Agent vs LangChain Evaluation Script
Compares Single Agent vs LangChain Multi-Agent performance with detailed metrics
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.langgraph_coordinator import LangGraphCoordinator
from agents.sentiment_agents import SentimentAgentFactory

class SingleVsLangChainEvaluator:
    """Evaluator comparing Single Agent vs LangChain system"""
    
    def __init__(self):
        """Initialize evaluator"""
        # Load config
        with open("config.json", 'r') as f:
            self.config = json.load(f)
        
        # Load dataset
        with open("evaluation/datasets/langchain_vs_single_dataset.json", 'r') as f:
            self.dataset = json.load(f)
    
    def evaluate_single_agent(self, category: str = "electronics") -> Dict[str, Any]:
        """Evaluate single agent performance"""
        print(f"\n=== 🤖 Single Agent Evaluation ({category}) ===")
        
        # Create single agent
        agent = SentimentAgentFactory.create_agent(
            agent_type="user_experience",
            config=self.config,
            max_tokens=200,
            product_category=category
        )
        
        results = []
        correct = 0
        total = 0
        confidence_scores = []
        start_time = time.time()
        
        for sample in self.dataset[category]:
            review = sample['review']
            ground_truth = sample['ground_truth']
            complexity = sample.get('complexity', 'unknown')
            
            try:
                # Analyze with single agent
                analysis = agent.analyze(review)
                predicted = analysis['sentiment']
                confidence = analysis['confidence']
                reasoning = analysis.get('reasoning', 'No reasoning provided')
                
                is_correct = ground_truth == predicted
                if is_correct:
                    correct += 1
                total += 1
                confidence_scores.append(confidence)
                
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': predicted,
                    'confidence': confidence,
                    'reasoning': reasoning[:200] + "..." if len(reasoning) > 200 else reasoning,
                    'correct': is_correct,
                    'complexity': complexity
                })
                
                status = "✅" if is_correct else "❌"
                print(f"  {status} {ground_truth} → {predicted} (conf: {confidence:.3f}) | {complexity}")
                
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': 'error',
                    'confidence': 0.0,
                    'reasoning': f'Error: {str(e)}',
                    'correct': False,
                    'complexity': complexity
                })
                total += 1
                confidence_scores.append(0.0)
        
        processing_time = time.time() - start_time
        accuracy = correct / total if total > 0 else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'processing_time': processing_time,
            'avg_confidence': avg_confidence,
            'max_confidence': max(confidence_scores) if confidence_scores else 0,
            'min_confidence': min(confidence_scores) if confidence_scores else 0,
            'results': results
        }
    
    def evaluate_langchain_system(self, category: str = "electronics") -> Dict[str, Any]:
        """Evaluate LangChain multi-agent system performance"""
        print(f"\n=== 🧠 LangChain Multi-Agent System ({category}) ===")
        
        # Create LangGraph coordinator
        coordinator = LangGraphCoordinator(
            config=self.config,
            product_category=category,
            department_types=["quality", "experience", "user_experience", "business", "technical"],
            max_tokens_per_department=150,
            max_discussion_rounds=3,
            disagreement_threshold=0.6
        )
        
        results = []
        correct = 0
        total = 0
        confidence_scores = []
        discussion_rounds = []
        start_time = time.time()
        
        for sample in self.dataset[category]:
            review = sample['review']
            ground_truth = sample['ground_truth']
            complexity = sample.get('complexity', 'unknown')
            
            try:
                # Analyze with LangGraph multi-agent system
                analysis_result = coordinator.run_analysis(review)
                
                # Extract data from result
                master_analysis = analysis_result.get('master_analysis', {})
                predicted = master_analysis.get('sentiment', 'neutral')
                confidence = master_analysis.get('confidence', 0.5)
                master_reasoning = master_analysis.get('reasoning', 'No reasoning provided')
                
                # Extract workflow metadata
                workflow_metadata = analysis_result.get('workflow_metadata', {})
                rounds = workflow_metadata.get('discussion_rounds', 0)
                consensus_reached = workflow_metadata.get('consensus_reached', True)
                disagreement_level = workflow_metadata.get('disagreement_level', 0.0)
                
                discussion_rounds.append(rounds)
                
                is_correct = ground_truth == predicted
                if is_correct:
                    correct += 1
                total += 1
                confidence_scores.append(confidence)
                
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': predicted,
                    'confidence': confidence,
                    'master_reasoning': master_reasoning[:300] + "..." if len(master_reasoning) > 300 else master_reasoning,
                    'discussion_rounds': rounds,
                    'consensus_reached': consensus_reached,
                    'disagreement_level': disagreement_level,
                    'correct': is_correct,
                    'complexity': complexity
                })
                
                status = "✅" if is_correct else "❌"
                print(f"  {status} {ground_truth} → {predicted} (conf: {confidence:.3f}, rounds: {rounds}) | {complexity}")
                
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': 'error',
                    'confidence': 0.0,
                    'master_reasoning': f'Error: {str(e)}',
                    'discussion_rounds': 0,
                    'consensus_reached': False,
                    'disagreement_level': 0.0,
                    'correct': False,
                    'complexity': complexity
                })
                total += 1
                confidence_scores.append(0.0)
                discussion_rounds.append(0)
        
        processing_time = time.time() - start_time
        accuracy = correct / total if total > 0 else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        avg_discussions = sum(discussion_rounds) / len(discussion_rounds) if discussion_rounds else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'processing_time': processing_time,
            'avg_confidence': avg_confidence,
            'max_confidence': max(confidence_scores) if confidence_scores else 0,
            'min_confidence': min(confidence_scores) if confidence_scores else 0,
            'avg_discussion_rounds': avg_discussions,
            'max_discussion_rounds': max(discussion_rounds) if discussion_rounds else 0,
            'results': results
        }
    
    def compare_approaches(self, category: str = "electronics") -> Dict[str, Any]:
        """Compare single vs LangChain approaches"""
        print(f"\n🔍 Comparing Single Agent vs LangChain for {category.upper()}")
        print("=" * 60)
        
        # Run evaluations
        single_result = self.evaluate_single_agent(category)
        langchain_result = self.evaluate_langchain_system(category)
        
        # Calculate comparisons
        accuracy_difference = langchain_result['accuracy'] - single_result['accuracy']
        accuracy_improvement_percent = (accuracy_difference / single_result['accuracy'] * 100) if single_result['accuracy'] > 0 else 0
        confidence_difference = langchain_result['avg_confidence'] - single_result['avg_confidence']
        time_ratio = langchain_result['processing_time'] / single_result['processing_time'] if single_result['processing_time'] > 0 else 1
        
        # Print summary
        print(f"\n📊 RESULTS SUMMARY")
        print("=" * 40)
        print(f"Single Agent:")
        print(f"  Accuracy: {single_result['accuracy']:.1%} ({single_result['correct']}/{single_result['total']})")
        print(f"  Avg Confidence: {single_result['avg_confidence']:.3f}")
        print(f"  Time: {single_result['processing_time']:.1f}s")
        
        print(f"\nLangChain System:")
        print(f"  Accuracy: {langchain_result['accuracy']:.1%} ({langchain_result['correct']}/{langchain_result['total']})")
        print(f"  Avg Confidence: {langchain_result['avg_confidence']:.3f}")
        print(f"  Time: {langchain_result['processing_time']:.1f}s")
        print(f"  Avg Discussion Rounds: {langchain_result['avg_discussion_rounds']:.1f}")
        
        print(f"\nComparison:")
        print(f"  Accuracy Difference: {accuracy_difference:+.1%} ({accuracy_improvement_percent:+.1f}%)")
        print(f"  Confidence Difference: {confidence_difference:+.3f}")
        print(f"  Time Ratio: {time_ratio:.1f}x")
        
        # Determine winner
        langchain_advantages = 0
        if langchain_result['accuracy'] > single_result['accuracy']:
            langchain_advantages += 1
        if langchain_result['avg_confidence'] > single_result['avg_confidence']:
            langchain_advantages += 1
        if langchain_result.get('avg_discussion_rounds', 0) > 0:
            langchain_advantages += 1  # Discussion capability
        
        print(f"\n🏆 WINNER: ", end="")
        if langchain_advantages >= 2:
            print("LangChain (superior analysis)")
        elif langchain_advantages == 1:
            print("Slight LangChain advantage")
        else:
            print("Single Agent (simplicity & speed)")
        
        return {
            'category': category,
            'single_agent': single_result,
            'langchain_system': langchain_result,
            'comparison': {
                'accuracy_difference': accuracy_difference,
                'accuracy_improvement_percent': accuracy_improvement_percent,
                'confidence_difference': confidence_difference,
                'time_ratio': time_ratio,
                'langchain_has_discussions': langchain_result.get('avg_discussion_rounds', 0) > 0
            }
        }
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all categories"""
        print("🚀 SINGLE AGENT vs LANGCHAIN EVALUATION")
        print("=" * 50)
        
        all_results = {}
        
        for category in self.dataset.keys():
            if self.dataset[category]:  # Skip empty categories
                result = self.compare_approaches(category)
                all_results[category] = result
        
        # Save results with metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"evaluation/results/single_vs_langchain_{timestamp}.json"
        
        final_results = {
            'test_metadata': {
                'workflows_compared': ['single_agent', 'langchain'],
                'test_date': datetime.now().isoformat(),
                'dataset_used': 'langchain_vs_single_dataset.json',
                'total_categories': len(all_results),
                'total_cases': sum(len(self.dataset[cat]) for cat in self.dataset if self.dataset[cat])
            },
            'results': all_results
        }
        
        with open(result_file, 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {result_file}")
        return final_results

def main():
    """Main evaluation function"""
    evaluator = SingleVsLangChainEvaluator()
    evaluator.run_full_evaluation()

if __name__ == "__main__":
    main() 