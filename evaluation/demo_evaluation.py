#!/usr/bin/env python3
"""
Demo Evaluation with Mock Data
Shows how the evaluation system works with simulated results
"""

import json
import sys
import os
import random
import time
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockSentimentAnalyzer:
    """Mock analyzer for demonstration"""
    
    def __init__(self, accuracy_rate: float = 0.75):
        self.accuracy_rate = accuracy_rate
        self.sentiments = ['negative', 'neutral', 'mixed', 'positive']
    
    def predict(self, review: str, ground_truth: str) -> dict:
        """Mock prediction with controlled accuracy"""
        # Simulate API delay
        time.sleep(0.1)
        
        # Randomly decide if prediction is correct based on accuracy rate
        if random.random() < self.accuracy_rate:
            predicted = ground_truth  # Correct prediction
            confidence = random.uniform(0.7, 0.95)
        else:
            # Wrong prediction
            predicted = random.choice([s for s in self.sentiments if s != ground_truth])
            confidence = random.uniform(0.5, 0.8)
        
        return {
            'sentiment': predicted,
            'confidence': confidence,
            'reasoning': f"Mock analysis based on: {review[:50]}..."
        }

def load_labeled_dataset():
    """Load evaluation dataset"""
    dataset_path = "evaluation/labeled_dataset.json"
    with open(dataset_path, 'r') as f:
        return json.load(f)

def evaluate_mock_system(category: str, single_accuracy: float = 0.76, multi_accuracy: float = 0.89):
    """Evaluate mock system with controlled accuracies"""
    
    print(f"\n MOCK EVALUATION: {category.upper()}")
    print("=" * 50)
    
    # Load dataset
    dataset = load_labeled_dataset()
    samples = dataset[category]
    
    # Create mock analyzers
    single_analyzer = MockSentimentAnalyzer(accuracy_rate=single_accuracy)
    multi_analyzer = MockSentimentAnalyzer(accuracy_rate=multi_accuracy)
    
    # Label encoding
    label_encoder = {'negative': 0, 'neutral': 1, 'mixed': 2, 'positive': 3}
    
    # Evaluate Single Agent
    print(f"\n Single Agent Evaluation...")
    single_results = []
    single_y_true = []
    single_y_pred = []
    single_confidences = []
    
    start_time = time.time()
    for sample in samples:
        result = single_analyzer.predict(sample['review'], sample['ground_truth'])
        
        single_results.append({
            'review': sample['review'],
            'ground_truth': sample['ground_truth'],
            'predicted': result['sentiment'],
            'confidence': result['confidence'],
            'correct': sample['ground_truth'] == result['sentiment']
        })
        
        single_y_true.append(label_encoder[sample['ground_truth']])
        single_y_pred.append(label_encoder[result['sentiment']])
        single_confidences.append(result['confidence'])
        
        print(f"   ✓ {sample['ground_truth']} -> {result['sentiment']} (conf: {result['confidence']:.2f})")
    
    single_time = time.time() - start_time
    
    # Evaluate Multi-Agent
    print(f"\n Multi-Agent Evaluation...")
    multi_results = []
    multi_y_true = []
    multi_y_pred = []
    multi_confidences = []
    
    start_time = time.time()
    for sample in samples:
        # Simulate multiple agents (with slightly better performance)
        agent_predictions = []
        for agent_name in ['quality', 'experience', 'user_experience', 'business']:
            agent_result = multi_analyzer.predict(sample['review'], sample['ground_truth'])
            agent_predictions.append(agent_result)
        
        # Simulate consensus (use best confidence prediction)
        best_prediction = max(agent_predictions, key=lambda x: x['confidence'])
        
        multi_results.append({
            'review': sample['review'],
            'ground_truth': sample['ground_truth'],
            'predicted': best_prediction['sentiment'],
            'confidence': best_prediction['confidence'],
            'correct': sample['ground_truth'] == best_prediction['sentiment'],
            'agents_used': 4,
            'discussion_rounds': random.randint(1, 2)
        })
        
        multi_y_true.append(label_encoder[sample['ground_truth']])
        multi_y_pred.append(label_encoder[best_prediction['sentiment']])
        multi_confidences.append(best_prediction['confidence'])
        
        print(f"   ✓ {sample['ground_truth']} -> {best_prediction['sentiment']} (conf: {best_prediction['confidence']:.2f})")
    
    multi_time = time.time() - start_time
    
    # Calculate metrics
    print(f"\n PERFORMANCE COMPARISON")
    print("-" * 60)
    
    # Single Agent Metrics
    single_accuracy_score = accuracy_score(single_y_true, single_y_pred)
    single_precision, single_recall, single_f1, _ = precision_recall_fscore_support(
        single_y_true, single_y_pred, average='weighted', zero_division=0
    )
    single_cm = confusion_matrix(single_y_true, single_y_pred)
    
    # Multi-Agent Metrics
    multi_accuracy_score = accuracy_score(multi_y_true, multi_y_pred)
    multi_precision, multi_recall, multi_f1, _ = precision_recall_fscore_support(
        multi_y_true, multi_y_pred, average='weighted', zero_division=0
    )
    multi_cm = confusion_matrix(multi_y_true, multi_y_pred)
    
    # Print comparison table
    metrics_data = [
        ('Accuracy', single_accuracy_score, multi_accuracy_score),
        ('Precision', single_precision, multi_precision),
        ('Recall', single_recall, multi_recall),
        ('F1-Score', single_f1, multi_f1),
        ('Avg Confidence', np.mean(single_confidences), np.mean(multi_confidences)),
        ('Processing Time', single_time, multi_time)
    ]
    
    print(f"{'Metric':<20} {'Single Agent':<15} {'Multi-Agent':<15} {'Improvement':<15}")
    print("-" * 70)
    
    for metric_name, single_val, multi_val in metrics_data:
        if metric_name == 'Processing Time':
            improvement = ((single_val - multi_val) / single_val) * 100 if single_val > 0 else 0
            improvement_str = f"{improvement:+.1f}%"
        else:
            improvement = ((multi_val - single_val) / single_val) * 100 if single_val > 0 else 0
            improvement_str = f"{improvement:+.1f}%"
        
        print(f"{metric_name:<20} {single_val:<15.3f} {multi_val:<15.3f} {improvement_str:<15}")
    
    # Error Analysis
    print(f"\n ERROR ANALYSIS")
    print("-" * 30)
    
    single_errors = [r for r in single_results if not r['correct']]
    multi_errors = [r for r in multi_results if not r['correct']]
    
    print(f"Single Agent errors: {len(single_errors)}/{len(samples)} ({len(single_errors)/len(samples)*100:.1f}%)")
    print(f"Multi-Agent errors: {len(multi_errors)}/{len(samples)} ({len(multi_errors)/len(samples)*100:.1f}%)")
    print(f"Error reduction: {len(single_errors) - len(multi_errors)} predictions improved")
    
    # Sample errors
    if multi_errors:
        print(f"\n Sample Multi-Agent Errors:")
        for i, error in enumerate(multi_errors[:2]):
            print(f"   {i+1}. Expected: {error['ground_truth']}, Got: {error['predicted']}")
            print(f"      Review: {error['review'][:80]}...")
    
    # Confusion Matrix
    print(f"\n CONFUSION MATRICES")
    print("-" * 30)
    
    labels = ['Negative', 'Neutral', 'Mixed', 'Positive']
    print(f"\nSingle Agent Confusion Matrix:")
    print(f"{'Actual/Predicted':<15} {' '.join([f'{l:>8}' for l in labels])}")
    for i, label in enumerate(labels):
        row = single_cm[i] if i < len(single_cm) else [0] * len(labels)
        print(f"{label:<15} {' '.join([f'{val:>8}' for val in row])}")
    
    print(f"\nMulti-Agent Confusion Matrix:")
    print(f"{'Actual/Predicted':<15} {' '.join([f'{l:>8}' for l in labels])}")
    for i, label in enumerate(labels):
        row = multi_cm[i] if i < len(multi_cm) else [0] * len(labels)
        print(f"{label:<15} {' '.join([f'{val:>8}' for val in row])}")
    
    return {
        'category': category,
        'sample_size': len(samples),
        'single_agent': {
            'accuracy': single_accuracy_score,
            'precision': single_precision,
            'recall': single_recall,
            'f1_score': single_f1,
            'avg_confidence': np.mean(single_confidences),
            'processing_time': single_time,
            'errors': len(single_errors)
        },
        'multi_agent': {
            'accuracy': multi_accuracy_score,
            'precision': multi_precision,
            'recall': multi_recall,
            'f1_score': multi_f1,
            'avg_confidence': np.mean(multi_confidences),
            'processing_time': multi_time,
            'errors': len(multi_errors)
        },
        'improvements': {
            'accuracy_improvement': ((multi_accuracy_score - single_accuracy_score) / single_accuracy_score) * 100,
            'error_reduction': len(single_errors) - len(multi_errors)
        }
    }

def run_comprehensive_demo():
    """Run comprehensive demo evaluation"""
    print(" COMPREHENSIVE MOCK EVALUATION DEMO")
    print("=" * 80)
    print("This demo simulates the evaluation with controlled accuracy rates")
    print("to demonstrate the metrics and comparison functionality.")
    print("=" * 80)
    
    # Load dataset to get categories
    dataset = load_labeled_dataset()
    categories = list(dataset.keys())
    
    all_results = {}
    
    # Different accuracy rates for different categories to show variety
    accuracy_configs = {
        'electronics': {'single': 0.75, 'multi': 0.875},
        'fashion': {'single': 0.80, 'multi': 0.90},
        'beauty_health': {'single': 0.70, 'multi': 0.85}
    }
    
    for category in categories:
        config = accuracy_configs.get(category, {'single': 0.76, 'multi': 0.89})
        result = evaluate_mock_system(
            category, 
            single_accuracy=config['single'],
            multi_accuracy=config['multi']
        )
        all_results[category] = result
    
    # Generate Summary Report
    print(f"\n FINAL SUMMARY REPORT")
    print("=" * 50)
    
    total_samples = sum(r['sample_size'] for r in all_results.values())
    avg_single_accuracy = np.mean([r['single_agent']['accuracy'] for r in all_results.values()])
    avg_multi_accuracy = np.mean([r['multi_agent']['accuracy'] for r in all_results.values()])
    avg_single_f1 = np.mean([r['single_agent']['f1_score'] for r in all_results.values()])
    avg_multi_f1 = np.mean([r['multi_agent']['f1_score'] for r in all_results.values()])
    
    total_single_errors = sum(r['single_agent']['errors'] for r in all_results.values())
    total_multi_errors = sum(r['multi_agent']['errors'] for r in all_results.values())
    
    accuracy_improvement = ((avg_multi_accuracy - avg_single_accuracy) / avg_single_accuracy) * 100
    f1_improvement = ((avg_multi_f1 - avg_single_f1) / avg_single_f1) * 100
    
    print(f" OVERALL PERFORMANCE (across {len(categories)} categories):")
    print(f"   Total test samples: {total_samples}")
    print(f"   Single Agent Accuracy: {avg_single_accuracy:.3f} ({total_single_errors} errors)")
    print(f"   Multi-Agent Accuracy:  {avg_multi_accuracy:.3f} ({total_multi_errors} errors)")
    print(f"   Accuracy Improvement:  +{accuracy_improvement:.1f}%")
    print(f"")
    print(f"   Single Agent F1-Score: {avg_single_f1:.3f}")
    print(f"   Multi-Agent F1-Score:  {avg_multi_f1:.3f}")
    print(f"   F1-Score Improvement:  +{f1_improvement:.1f}%")
    print(f"")
    print(f"   Error reduction: {total_single_errors - total_multi_errors} predictions improved")
    
    # Save results
    summary = {
        'evaluation_type': 'mock_demo',
        'total_samples': total_samples,
        'overall_metrics': {
            'single_agent_accuracy': avg_single_accuracy,
            'multi_agent_accuracy': avg_multi_accuracy,
            'accuracy_improvement_percent': accuracy_improvement,
            'single_agent_f1': avg_single_f1,
            'multi_agent_f1': avg_multi_f1,
            'f1_improvement_percent': f1_improvement,
            'total_single_errors': total_single_errors,
            'total_multi_errors': total_multi_errors,
            'error_reduction': total_single_errors - total_multi_errors
        },
        'detailed_results': all_results
    }
    
    # Create evaluation directory if it doesn't exist
    os.makedirs('evaluation', exist_ok=True)
    
    with open('evaluation/mock_evaluation_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n Mock evaluation results saved: evaluation/mock_evaluation_results.json")
    print(f"\n Demo evaluation completed!")
    print(f" This demonstrates the evaluation framework with {accuracy_improvement:.1f}% improvement")
    print(f" To run with real API, set up OpenAI API key and use: python evaluation/evaluation_script.py")
    
    return summary

if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    # Run demo
    results = run_comprehensive_demo() 