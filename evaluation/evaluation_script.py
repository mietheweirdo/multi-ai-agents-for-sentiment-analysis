#!/usr/bin/env python3
"""
Comprehensive Evaluation Script for Multi-Agent Sentiment Analysis System
Measures accuracy, precision, recall, F1-score against ground truth
Compares Single Agent vs Multi-Agent performance
"""

import json
import os
import sys
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.enhanced_coordinator import EnhancedCoordinatorAgent
from agents.sentiment_agents import SentimentAgentFactory
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class EvaluationResult:
    """Container for evaluation results"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: np.ndarray
    detailed_results: List[Dict[str, Any]]
    processing_time: float
    confidence_scores: List[float]
    
class SentimentEvaluator:
    """Comprehensive sentiment analysis evaluator"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize evaluator with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Load labeled dataset
        self.dataset = self._load_labeled_dataset()
        
        # Sentiment mapping for consistency
        self.sentiment_mapping = {
            'positive': 'positive',
            'negative': 'negative', 
            'neutral': 'neutral',
            'mixed': 'mixed'
        }
        
        # Label encoding for sklearn metrics
        self.label_encoder = {'negative': 0, 'neutral': 1, 'mixed': 2, 'positive': 3}
        self.label_decoder = {v: k for k, v in self.label_encoder.items()}
    
    def _load_labeled_dataset(self) -> Dict[str, List[Dict]]:
        """Load labeled evaluation dataset"""
        dataset_path = os.path.join(os.path.dirname(__file__), 'labeled_dataset.json')
        with open(dataset_path, 'r') as f:
            return json.load(f)
    
    def evaluate_single_agent(self, product_category: str = "electronics", 
                            max_tokens: int = 150) -> EvaluationResult:
        """Evaluate single agent approach"""
        print(f"\nEvaluating Single Agent ({product_category})...")
        
        # Create single user_experience agent
        agent = SentimentAgentFactory.create_agent(
            agent_type="user_experience",
            config=self.config,
            max_tokens=max_tokens,
            product_category=product_category
        )
        
        results = []
        y_true = []
        y_pred = []
        confidence_scores = []
        
        start_time = time.time()
        
        for sample in self.dataset[product_category]:
            review = sample['review']
            ground_truth = sample['ground_truth']
            
            try:
                # Analyze with single agent
                analysis = agent.analyze(review)
                predicted_sentiment = analysis['sentiment']
                confidence = analysis['confidence']
                
                # Store results
                results.append({
                    'review': review,
                    'ground_truth': ground_truth,
                    'predicted': predicted_sentiment,
                    'confidence': confidence,
                    'correct': ground_truth == predicted_sentiment
                })
                
                y_true.append(self.label_encoder[ground_truth])
                y_pred.append(self.label_encoder.get(predicted_sentiment, 1))  # Default to neutral
                confidence_scores.append(confidence)
                
                print(f"   ✓ {ground_truth} -> {predicted_sentiment} (conf: {confidence:.2f})")
                
            except Exception as e:
                print(f"    Error analyzing review: {e}")
                # Add as incorrect prediction
                results.append({
                    'review': review,
                    'ground_truth': ground_truth,
                    'predicted': 'neutral',
                    'confidence': 0.5,
                    'correct': False
                })
                y_true.append(self.label_encoder[ground_truth])
                y_pred.append(1)  # neutral
                confidence_scores.append(0.5)
        
        processing_time = time.time() - start_time
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        cm = confusion_matrix(y_true, y_pred)
        
        return EvaluationResult(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=cm,
            detailed_results=results,
            processing_time=processing_time,
            confidence_scores=confidence_scores
        )
    
    def evaluate_multi_agent(self, product_category: str = "electronics",
                           agent_types: List[str] = None,
                           max_tokens_per_agent: int = 150) -> EvaluationResult:
        """Evaluate multi-agent approach"""
        print(f"\nEvaluating Multi-Agent System ({product_category})...")
        
        if agent_types is None:
            agent_types = ["quality", "experience", "user_experience", "business"]
        
        # Create multi-agent coordinator
        coordinator = EnhancedCoordinatorAgent(
            config=self.config,
            product_category=product_category,
            agent_types=agent_types,
            max_tokens_per_agent=max_tokens_per_agent
        )
        
        results = []
        y_true = []
        y_pred = []
        confidence_scores = []
        
        start_time = time.time()
        
        for sample in self.dataset[product_category]:
            review = sample['review']
            ground_truth = sample['ground_truth']
            
            try:
                # Analyze with multi-agent system
                analysis_result = coordinator.run_workflow(
                    reviews=[review],
                    product_category=product_category
                )
                
                predicted_sentiment = analysis_result['consensus']['overall_sentiment']
                confidence = analysis_result['consensus']['overall_confidence']
                
                # Store results
                results.append({
                    'review': review,
                    'ground_truth': ground_truth,
                    'predicted': predicted_sentiment,
                    'confidence': confidence,
                    'correct': ground_truth == predicted_sentiment,
                    'agent_analyses': analysis_result.get('agent_analyses', []),
                    'discussion_rounds': analysis_result['analysis_metadata'].get('discussion_rounds', 0)
                })
                
                y_true.append(self.label_encoder[ground_truth])
                y_pred.append(self.label_encoder.get(predicted_sentiment, 1))
                confidence_scores.append(confidence)
                
                print(f"   ✓ {ground_truth} -> {predicted_sentiment} (conf: {confidence:.2f})")
                
            except Exception as e:
                print(f"    Error analyzing review: {e}")
                # Add as incorrect prediction
                results.append({
                    'review': review,
                    'ground_truth': ground_truth,
                    'predicted': 'neutral',
                    'confidence': 0.5,
                    'correct': False
                })
                y_true.append(self.label_encoder[ground_truth])
                y_pred.append(1)
                confidence_scores.append(0.5)
        
        processing_time = time.time() - start_time
        
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        cm = confusion_matrix(y_true, y_pred)
        
        return EvaluationResult(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=cm,
            detailed_results=results,
            processing_time=processing_time,
            confidence_scores=confidence_scores
        )
    
    def compare_approaches(self, product_category: str = "electronics") -> Dict[str, Any]:
        """Compare single agent vs multi-agent approaches"""
        print(f"\nComprehensive Evaluation: {product_category.upper()}")
        print("=" * 60)
        
        # Evaluate both approaches
        single_result = self.evaluate_single_agent(product_category)
        multi_result = self.evaluate_multi_agent(product_category)
        
        # Print comparison
        print(f"\nPERFORMANCE COMPARISON")
        print("-" * 40)
        print(f"{'Metric':<20} {'Single Agent':<15} {'Multi-Agent':<15} {'Improvement':<15}")
        print("-" * 70)
        
        metrics = [
            ('Accuracy', single_result.accuracy, multi_result.accuracy),
            ('Precision', single_result.precision, multi_result.precision),
            ('Recall', single_result.recall, multi_result.recall),
            ('F1-Score', single_result.f1_score, multi_result.f1_score),
            ('Avg Confidence', statistics.mean(single_result.confidence_scores), 
             statistics.mean(multi_result.confidence_scores)),
            ('Processing Time', single_result.processing_time, multi_result.processing_time)
        ]
        
        improvements = []
        for metric_name, single_val, multi_val in metrics:
            if metric_name == 'Processing Time':
                improvement = ((single_val - multi_val) / single_val) * 100  # Negative is slower
                improvement_str = f"{improvement:+.1f}%"
            else:
                improvement = ((multi_val - single_val) / single_val) * 100
                improvement_str = f"{improvement:+.1f}%"
            
            improvements.append(improvement)
            print(f"{metric_name:<20} {single_val:<15.3f} {multi_val:<15.3f} {improvement_str:<15}")
        
        # Statistical significance (basic)
        print(f"\nDETAILED ANALYSIS")
        print("-" * 40)
        
        # Count correct predictions
        single_correct = sum(1 for r in single_result.detailed_results if r['correct'])
        multi_correct = sum(1 for r in multi_result.detailed_results if r['correct'])
        total_samples = len(single_result.detailed_results)
        
        print(f"Total samples: {total_samples}")
        print(f"Single Agent correct: {single_correct}/{total_samples} ({single_correct/total_samples*100:.1f}%)")
        print(f"Multi-Agent correct: {multi_correct}/{total_samples} ({multi_correct/total_samples*100:.1f}%)")
        print(f"Improvement: +{multi_correct - single_correct} predictions ({((multi_correct - single_correct)/total_samples)*100:.1f}%)")
        
        # Confidence analysis
        print(f"\nCONFIDENCE ANALYSIS")
        print("-" * 40)
        print(f"Single Agent avg confidence: {statistics.mean(single_result.confidence_scores):.3f}")
        print(f"Multi-Agent avg confidence: {statistics.mean(multi_result.confidence_scores):.3f}")
        
        # Error analysis
        print(f"\nERROR ANALYSIS")
        print("-" * 40)
        
        single_errors = [r for r in single_result.detailed_results if not r['correct']]
        multi_errors = [r for r in multi_result.detailed_results if not r['correct']]
        
        print(f"Single Agent errors: {len(single_errors)}")
        print(f"Multi-Agent errors: {len(multi_errors)}")
        
        # Show sample errors
        if multi_errors:
            print(f"\n Sample Multi-Agent Errors:")
            for i, error in enumerate(multi_errors[:2]):  # Show first 2 errors
                print(f"   {i+1}. Expected: {error['ground_truth']}, Got: {error['predicted']}")
                print(f"      Review: {error['review'][:100]}...")
        
        return {
            'single_agent': {
                'accuracy': single_result.accuracy,
                'precision': single_result.precision,
                'recall': single_result.recall,
                'f1_score': single_result.f1_score,
                'avg_confidence': statistics.mean(single_result.confidence_scores),
                'processing_time': single_result.processing_time
            },
            'multi_agent': {
                'accuracy': multi_result.accuracy,
                'precision': multi_result.precision,
                'recall': multi_result.recall,
                'f1_score': multi_result.f1_score,
                'avg_confidence': statistics.mean(multi_result.confidence_scores),
                'processing_time': multi_result.processing_time
            },
            'improvements': {
                'accuracy_improvement': improvements[0],
                'precision_improvement': improvements[1],
                'recall_improvement': improvements[2],
                'f1_improvement': improvements[3],
                'confidence_improvement': improvements[4]
            },
            'sample_size': total_samples,
            'single_correct': single_correct,
            'multi_correct': multi_correct
        }
    
    def generate_confusion_matrix_plot(self, result: EvaluationResult, title: str, save_path: str = None):
        """Generate confusion matrix visualization"""
        plt.figure(figsize=(8, 6))
        
        labels = ['Negative', 'Neutral', 'Mixed', 'Positive']
        sns.heatmap(result.confusion_matrix, annot=True, fmt='d', cmap='Blues',
                   xticklabels=labels, yticklabels=labels)
        
        plt.title(f'Confusion Matrix - {title}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"    Confusion matrix saved: {save_path}")
        
        plt.show()
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation across all product categories"""
        print(" COMPREHENSIVE MULTI-AGENT SENTIMENT ANALYSIS EVALUATION")
        print("=" * 80)
        
        all_results = {}
        
        # Evaluate each product category
        for category in self.dataset.keys():
            print(f"\n Evaluating {category.upper()} category...")
            try:
                comparison = self.compare_approaches(category)
                all_results[category] = comparison
                
                # Save detailed results
                output_file = f"evaluation/results_{category}.json"
                with open(output_file, 'w') as f:
                    json.dump(comparison, f, indent=2)
                print(f"    Results saved: {output_file}")
                
            except Exception as e:
                print(f"    Error evaluating {category}: {e}")
                all_results[category] = {'error': str(e)}
        
        # Generate summary report
        self._generate_summary_report(all_results)
        
        return all_results
    
    def _generate_summary_report(self, results: Dict[str, Any]):
        """Generate comprehensive summary report"""
        print(f"\n FINAL SUMMARY REPORT")
        print("=" * 50)
        
        # Aggregate metrics
        categories = [k for k in results.keys() if 'error' not in results[k]]
        
        if not categories:
            print(" No successful evaluations to summarize")
            return
        
        # Calculate averages
        avg_single_accuracy = statistics.mean([results[c]['single_agent']['accuracy'] for c in categories])
        avg_multi_accuracy = statistics.mean([results[c]['multi_agent']['accuracy'] for c in categories])  
        avg_single_f1 = statistics.mean([results[c]['single_agent']['f1_score'] for c in categories])
        avg_multi_f1 = statistics.mean([results[c]['multi_agent']['f1_score'] for c in categories])
        
        accuracy_improvement = ((avg_multi_accuracy - avg_single_accuracy) / avg_single_accuracy) * 100
        f1_improvement = ((avg_multi_f1 - avg_single_f1) / avg_single_f1) * 100
        
        print(f" OVERALL PERFORMANCE (across {len(categories)} categories):")
        print(f"   Single Agent Accuracy: {avg_single_accuracy:.3f}")
        print(f"   Multi-Agent Accuracy:  {avg_multi_accuracy:.3f}")
        print(f"   Accuracy Improvement:  +{accuracy_improvement:.1f}%")
        print(f"")
        print(f"   Single Agent F1-Score: {avg_single_f1:.3f}")
        print(f"   Multi-Agent F1-Score:  {avg_multi_f1:.3f}")
        print(f"   F1-Score Improvement:  +{f1_improvement:.1f}%")
        
        # Total samples
        total_samples = sum([results[c]['sample_size'] for c in categories])
        total_single_correct = sum([results[c]['single_correct'] for c in categories])
        total_multi_correct = sum([results[c]['multi_correct'] for c in categories])
        
        print(f"\n TOTAL STATISTICS:")
        print(f"   Total test samples: {total_samples}")
        print(f"   Single Agent correct: {total_single_correct}/{total_samples}")
        print(f"   Multi-Agent correct: {total_multi_correct}/{total_samples}")
        print(f"   Net improvement: +{total_multi_correct - total_single_correct} predictions")
        
        # Save summary
        summary = {
            'evaluation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'categories_evaluated': categories,
            'total_samples': total_samples,
            'overall_metrics': {
                'single_agent_accuracy': avg_single_accuracy,
                'multi_agent_accuracy': avg_multi_accuracy,
                'accuracy_improvement_percent': accuracy_improvement,
                'single_agent_f1': avg_single_f1,
                'multi_agent_f1': avg_multi_f1,
                'f1_improvement_percent': f1_improvement
            },
            'detailed_results': results
        }
        
        with open('evaluation/comprehensive_evaluation_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n Comprehensive summary saved: evaluation/comprehensive_evaluation_summary.json")

if __name__ == "__main__":
    # Run comprehensive evaluation
    evaluator = SentimentEvaluator()
    
    # Run full evaluation
    results = evaluator.run_comprehensive_evaluation()
    
    print(f"\n Evaluation completed! Check the evaluation/ directory for detailed results.") 