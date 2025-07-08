#!/usr/bin/env python3
"""
Visual Workflow Comparison: Manual vs LangChain
Comprehensive evaluation with beautiful tables and detailed metrics
"""

import json
import time
import sys
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd
from tabulate import tabulate
from collections import defaultdict
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import both workflows
from workflow_manager import analyze_review as manual_analyze
from agents.langgraph_coordinator import analyze_with_langgraph

class VisualWorkflowComparator:
    """Visual comparison of Manual vs LangChain workflows with comprehensive metrics"""
    
    def __init__(self):
        """Initialize visual comparator"""
        # Load config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        # Comprehensive test dataset based on workflow_comparison_summary.md
        self.test_cases = [
            {
                "id": "CONFLICT_001",
                "name": "Quality vs Service Conflict",
                "review": "My new facial cleansing brush looks amazing and came in a beautiful package. The delivery was super fast and the team sent me a thank you card! But after three uses, I noticed redness and skin irritation that took days to calm down. I didn’t even bother asking for support after that — I just stopped using it.",
                "category": "electronics",
                "expected_sentiment": "negative",
                "conflict_type": "quality_vs_service",
                "complexity": "high"
            }
        ]
        
        # Initialize results storage
        self.results = {
            'manual': [],
            'langchain': []
        }
        
        # Metrics tracking
        self.metrics = {
            'manual': defaultdict(list),
            'langchain': defaultdict(list)
        }
        
    def run_comprehensive_evaluation(self):
        """Run comprehensive evaluation with detailed metrics"""
        
        print("🚀 STARTING COMPREHENSIVE WORKFLOW EVALUATION")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run all test cases
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📋 TEST CASE {i}/{len(self.test_cases)}: {test_case['name']}")
            print("-" * 60)
            
            result = self.run_single_test(test_case)
            self.store_results(test_case, result)
            
            # Progress indicator
            progress = i / len(self.test_cases) * 100
            print(f"Progress: {progress:.1f}% complete")
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print(f"\n✅ EVALUATION COMPLETED")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Test Cases: {len(self.test_cases)}")
        
        # Generate comprehensive report
        self.generate_visual_report()
        
    def run_single_test(self, test_case: Dict) -> Dict:
        """Run a single test case comparison"""
        
        review = test_case['review']
        category = test_case['category']
        
        print(f"Review: {review}")
        print(f"Category: {category}")
        print(f"Expected: {test_case['expected_sentiment']}")
        print(f"Complexity: {test_case['complexity']}")
        
        results = {
            'test_case': test_case,
            'manual': None,
            'langchain': None
        }
        
        # Test Manual Workflow
        print(f"\n🔧 MANUAL WORKFLOW:")
        try:
            manual_start = time.time()
            manual_result = manual_analyze(review, product_category=category)
            manual_time = time.time() - manual_start
            
            manual_data = {
                'result': manual_result,
                'execution_time': manual_time,
                'error': None,
                'sentiment': manual_result.get('master_analysis', {}).get('sentiment', 'unknown'),
                'confidence': manual_result.get('master_analysis', {}).get('confidence', 0.0),
                'reasoning': manual_result.get('master_analysis', {}).get('reasoning', ''),
                'discussion_rounds': 0,
                'consensus_reached': True,
                'disagreement_level': 0.0
            }
            
            results['manual'] = manual_data
            
            print(f"  ✅ Sentiment: {manual_data['sentiment']}")
            print(f"  ✅ Confidence: {manual_data['confidence']:.3f}")
            print(f"  ✅ Time: {manual_data['execution_time']:.3f}s")
            print(f"  ✅ Reasoning: {manual_data['reasoning']}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results['manual'] = {
                'result': None,
                'execution_time': 0,
                'error': str(e),
                'sentiment': 'error',
                'confidence': 0.0,
                'reasoning': '',
                'discussion_rounds': 0,
                'consensus_reached': False,
                'disagreement_level': 0.0
            }
        
        # Test LangChain Workflow  
        print(f"\n🚀 LANGCHAIN WORKFLOW:")
        try:
            langchain_start = time.time()
            langchain_result = analyze_with_langgraph(
                review=review,
                product_category=category,
                config=self.config,
                max_discussion_rounds=5,
                disagreement_threshold=0.1
            )
            langchain_time = time.time() - langchain_start
            
            workflow_metadata = langchain_result.get('workflow_metadata', {})
            
            langchain_data = {
                'result': langchain_result,
                'execution_time': langchain_time,
                'error': None,
                'sentiment': langchain_result.get('master_analysis', {}).get('sentiment', 'unknown'),
                'confidence': langchain_result.get('master_analysis', {}).get('confidence', 0.0),
                'reasoning': langchain_result.get('master_analysis', {}).get('reasoning', ''),
                'discussion_rounds': workflow_metadata.get('discussion_rounds', 0),
                'consensus_reached': workflow_metadata.get('consensus_reached', True),
                'disagreement_level': workflow_metadata.get('disagreement_level', 0.0),
                'discussion_messages': langchain_result.get('discussion_messages', [])
            }
            
            results['langchain'] = langchain_data
            
            print(f"  ✅ Sentiment: {langchain_data['sentiment']}")
            print(f"  ✅ Confidence: {langchain_data['confidence']:.3f}")
            print(f"  ✅ Time: {langchain_data['execution_time']:.3f}s")
            print(f"  ✅ Discussion Rounds: {langchain_data['discussion_rounds']}")
            print(f"  ✅ Consensus: {langchain_data['consensus_reached']}")
            print(f"  ✅ Disagreement: {langchain_data['disagreement_level']:.3f}")
            print(f"  ✅ Reasoning: {langchain_data['reasoning']}")
            
            # Show discussion messages
            if langchain_data['discussion_messages']:
                print(f"  📝 Discussion Messages ({len(langchain_data['discussion_messages'])} total):")
                for i, msg in enumerate(langchain_data['discussion_messages'], 1):
                    print(f"    {i}. {msg}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results['langchain'] = {
                'result': None,
                'execution_time': 0,
                'error': str(e),
                'sentiment': 'error',
                'confidence': 0.0,
                'reasoning': '',
                'discussion_rounds': 0,
                'consensus_reached': False,
                'disagreement_level': 0.0,
                'discussion_messages': []
            }
        
        return results
    
    def store_results(self, test_case: Dict, results: Dict):
        """Store results for later analysis"""
        
        # Store detailed results
        self.results['manual'].append(results['manual'])
        self.results['langchain'].append(results['langchain'])
        
        # Track metrics
        for workflow in ['manual', 'langchain']:
            if results[workflow] and results[workflow]['error'] is None:
                data = results[workflow]
                
                # Accuracy (compared to expected)
                is_correct = data['sentiment'] == test_case['expected_sentiment']
                self.metrics[workflow]['accuracy'].append(is_correct)
                
                # Performance metrics
                self.metrics[workflow]['execution_time'].append(data['execution_time'])
                self.metrics[workflow]['confidence'].append(data['confidence'])
                self.metrics[workflow]['discussion_rounds'].append(data['discussion_rounds'])
                self.metrics[workflow]['consensus_reached'].append(data['consensus_reached'])
                self.metrics[workflow]['disagreement_level'].append(data['disagreement_level'])
                self.metrics[workflow]['reasoning_length'].append(len(data['reasoning']))
                
                # Complexity handling
                self.metrics[workflow]['complexity'].append(test_case['complexity'])
                
                # Sentiment distribution
                self.metrics[workflow]['sentiment_distribution'].append(data['sentiment'])
                
                # Success rate
                self.metrics[workflow]['success_rate'].append(True)
            else:
                self.metrics[workflow]['success_rate'].append(False)
    
    def generate_visual_report(self):
        """Generate comprehensive visual report with tables"""
        
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE EVALUATION REPORT")
        print(f"🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        
        # 1. Executive Summary Table
        self.print_executive_summary()
        
        # 2. Detailed Metrics Comparison
        self.print_detailed_metrics()
        
        # 3. Performance Analysis
        self.print_performance_analysis()
        
        # 4. Accuracy Breakdown
        self.print_accuracy_breakdown()
        
        # 5. Detailed Test Results
        self.print_detailed_results()
        
        # 6. Error Analysis
        self.print_error_analysis()
        
        # 7. Recommendations
        self.print_recommendations()
    
    def print_executive_summary(self):
        """Print executive summary table"""
        
        print("\n📋 EXECUTIVE SUMMARY")
        print("-" * 50)
        
        # Calculate summary metrics
        summary_data = []
        
        for workflow in ['manual', 'langchain']:
            if self.metrics[workflow]['success_rate']:
                accuracy = np.mean(self.metrics[workflow]['accuracy']) * 100
                avg_time = np.mean(self.metrics[workflow]['execution_time'])
                avg_confidence = np.mean(self.metrics[workflow]['confidence'])
                success_rate = np.mean(self.metrics[workflow]['success_rate']) * 100
                avg_discussion = np.mean(self.metrics[workflow]['discussion_rounds'])
                
                summary_data.append([
                    workflow.upper(),
                    f"{accuracy:.1f}%",
                    f"{avg_time:.3f}s",
                    f"{avg_confidence:.3f}",
                    f"{success_rate:.1f}%",
                    f"{avg_discussion:.1f}"
                ])
        
        headers = ["Workflow", "Accuracy", "Avg Time", "Avg Confidence", "Success Rate", "Avg Discussion"]
        print(tabulate(summary_data, headers=headers, tablefmt="grid"))
    
    def print_detailed_metrics(self):
        """Print detailed metrics comparison"""
        
        print("\n📊 DETAILED METRICS COMPARISON")
        print("-" * 50)
        
        metrics_data = []
        
        for workflow in ['manual', 'langchain']:
            if self.metrics[workflow]['success_rate']:
                # Statistical metrics
                accuracy_scores = self.metrics[workflow]['accuracy']
                time_scores = self.metrics[workflow]['execution_time']
                confidence_scores = self.metrics[workflow]['confidence']
                
                metrics_data.append([
                    workflow.upper(),
                    f"{np.mean(accuracy_scores)*100:.1f}%",
                    f"{np.std(accuracy_scores)*100:.1f}%",
                    f"{np.mean(time_scores):.3f}s",
                    f"{np.std(time_scores):.3f}s",
                    f"{np.mean(confidence_scores):.3f}",
                    f"{np.std(confidence_scores):.3f}",
                    f"{np.min(confidence_scores):.3f}",
                    f"{np.max(confidence_scores):.3f}"
                ])
        
        headers = [
            "Workflow", "Accuracy Mean", "Accuracy Std", 
            "Time Mean", "Time Std", "Conf Mean", "Conf Std", "Conf Min", "Conf Max"
        ]
        print(tabulate(metrics_data, headers=headers, tablefmt="grid"))
    
    def print_performance_analysis(self):
        """Print performance analysis"""
        
        print("\n⚡ PERFORMANCE ANALYSIS")
        print("-" * 50)
        
        perf_data = []
        
        for workflow in ['manual', 'langchain']:
            if self.metrics[workflow]['success_rate']:
                times = self.metrics[workflow]['execution_time']
                discussions = self.metrics[workflow]['discussion_rounds']
                consensus = self.metrics[workflow]['consensus_reached']
                
                perf_data.append([
                    workflow.upper(),
                    f"{np.min(times):.3f}s",
                    f"{np.max(times):.3f}s",
                    f"{np.mean(times):.3f}s",
                    f"{np.median(times):.3f}s",
                    f"{np.max(discussions):.0f}",
                    f"{np.mean(consensus)*100:.1f}%"
                ])
        
        headers = ["Workflow", "Min Time", "Max Time", "Mean Time", "Median Time", "Max Discussions", "Consensus Rate"]
        print(tabulate(perf_data, headers=headers, tablefmt="grid"))
        
        # Speed comparison
        if len(self.metrics['manual']['execution_time']) > 0 and len(self.metrics['langchain']['execution_time']) > 0:
            manual_avg = np.mean(self.metrics['manual']['execution_time'])
            langchain_avg = np.mean(self.metrics['langchain']['execution_time'])
            speedup = langchain_avg / manual_avg if manual_avg > 0 else 0
            
            print(f"\n⚡ Speed Analysis:")
            print(f"  Manual Average: {manual_avg:.3f}s")
            print(f"  LangChain Average: {langchain_avg:.3f}s")
            print(f"  LangChain is {speedup:.1f}x {'slower' if speedup > 1 else 'faster'} than Manual")
    
    def print_accuracy_breakdown(self):
        """Print accuracy breakdown by categories"""
        
        print("\n🎯 ACCURACY BREAKDOWN")
        print("-" * 50)
        
        # By complexity
        complexity_data = []
        for complexity in ['low', 'medium', 'high']:
            for workflow in ['manual', 'langchain']:
                if self.metrics[workflow]['complexity']:
                    # Filter by complexity
                    complexity_indices = [i for i, c in enumerate(self.metrics[workflow]['complexity']) if c == complexity]
                    if complexity_indices:
                        complexity_accuracies = [self.metrics[workflow]['accuracy'][i] for i in complexity_indices]
                        accuracy = np.mean(complexity_accuracies) * 100
                        count = len(complexity_accuracies)
                        
                        complexity_data.append([
                            complexity.upper(),
                            workflow.upper(),
                            f"{accuracy:.1f}%",
                            f"{count}"
                        ])
        
        headers = ["Complexity", "Workflow", "Accuracy", "Count"]
        print(tabulate(complexity_data, headers=headers, tablefmt="grid"))
        
        # Sentiment distribution
        print(f"\n📈 SENTIMENT DISTRIBUTION:")
        for workflow in ['manual', 'langchain']:
            if self.metrics[workflow]['sentiment_distribution']:
                sentiments = self.metrics[workflow]['sentiment_distribution']
                from collections import Counter
                dist = Counter(sentiments)
                print(f"  {workflow.upper()}: {dict(dist)}")
    
    def print_detailed_results(self):
        """Print detailed test results"""
        
        print("\n📋 DETAILED TEST RESULTS")
        print("-" * 50)
        
        results_data = []
        
        for i, test_case in enumerate(self.test_cases):
            manual_result = self.results['manual'][i]
            langchain_result = self.results['langchain'][i]
            
            results_data.append([
                test_case['id'],
                test_case['name'][:25] + "...",
                test_case['expected_sentiment'],
                manual_result['sentiment'] if manual_result else 'ERROR',
                langchain_result['sentiment'] if langchain_result else 'ERROR',
                f"{manual_result['confidence']:.2f}" if manual_result else '0.00',
                f"{langchain_result['confidence']:.2f}" if langchain_result else '0.00',
                f"{manual_result['execution_time']:.3f}s" if manual_result else '0.000s',
                f"{langchain_result['execution_time']:.3f}s" if langchain_result else '0.000s'
            ])
        
        headers = [
            "ID", "Test Name", "Expected", "Manual", "LangChain", 
            "M_Conf", "L_Conf", "M_Time", "L_Time"
        ]
        print(tabulate(results_data, headers=headers, tablefmt="grid"))
        
        # Show full reasoning for all cases
        print(f"\n🧠 DETAILED REASONING FOR ALL CASES:")
        for i, test_case in enumerate(self.test_cases):
            print(f"\n{'-'*80}")
            print(f"{test_case['id']}: {test_case['name']}")
            print(f"Review: {test_case['review']}")
            print(f"Expected: {test_case['expected_sentiment']} | Complexity: {test_case['complexity']}")
            
            manual_result = self.results['manual'][i]
            langchain_result = self.results['langchain'][i]
            
            if manual_result and manual_result['reasoning']:
                print(f"\nMANUAL REASONING:")
                print(f"{manual_result['reasoning']}")
            else:
                print(f"\nMANUAL REASONING: No reasoning available")
            
            if langchain_result and langchain_result['reasoning']:
                print(f"\nLANGCHAIN REASONING:")
                print(f"{langchain_result['reasoning']}")
            else:
                print(f"\nLANGCHAIN REASONING: No reasoning available")
            
            if langchain_result and langchain_result.get('discussion_messages'):
                print(f"\nDISCUSSION MESSAGES:")
                for j, msg in enumerate(langchain_result['discussion_messages'], 1):
                    print(f"  {j}. {msg}")
            else:
                print(f"\nDISCUSSION MESSAGES: No discussion occurred")
    
    def print_error_analysis(self):
        """Print error analysis"""
        
        print("\n❌ ERROR ANALYSIS")
        print("-" * 50)
        
        error_data = []
        
        for workflow in ['manual', 'langchain']:
            successes = sum(self.metrics[workflow]['success_rate'])
            total = len(self.metrics[workflow]['success_rate'])
            failures = total - successes
            
            error_data.append([
                workflow.upper(),
                f"{successes}",
                f"{failures}",
                f"{successes/total*100:.1f}%" if total > 0 else "0%"
            ])
        
        headers = ["Workflow", "Successes", "Failures", "Success Rate"]
        print(tabulate(error_data, headers=headers, tablefmt="grid"))
        
        # Show actual errors
        for workflow in ['manual', 'langchain']:
            errors = [r for r in self.results[workflow] if r and r.get('error')]
            if errors:
                print(f"\n❌ {workflow.upper()} ERRORS:")
                for i, error in enumerate(errors, 1):
                    print(f"  {i}. {error['error']}")
    
    def print_recommendations(self):
        """Print recommendations based on analysis"""
        
        print("\n💡 RECOMMENDATIONS")
        print("-" * 50)
        
        # Calculate key metrics
        manual_accuracy = np.mean(self.metrics['manual']['accuracy']) * 100 if self.metrics['manual']['accuracy'] else 0
        langchain_accuracy = np.mean(self.metrics['langchain']['accuracy']) * 100 if self.metrics['langchain']['accuracy'] else 0
        
        manual_time = np.mean(self.metrics['manual']['execution_time']) if self.metrics['manual']['execution_time'] else 0
        langchain_time = np.mean(self.metrics['langchain']['execution_time']) if self.metrics['langchain']['execution_time'] else 0
        
        print(f"Based on comprehensive evaluation of {len(self.test_cases)} test cases:")
        print()
        
        if langchain_accuracy > manual_accuracy:
            print(f"✅ ACCURACY: LangChain shows {langchain_accuracy - manual_accuracy:.1f}% better accuracy")
            print(f"   LangChain: {langchain_accuracy:.1f}% vs Manual: {manual_accuracy:.1f}%")
        else:
            print(f"⚠️  ACCURACY: Manual shows {manual_accuracy - langchain_accuracy:.1f}% better accuracy")
            print(f"   Manual: {manual_accuracy:.1f}% vs LangChain: {langchain_accuracy:.1f}%")
        
        print()
        
        if langchain_time > manual_time:
            speedup = langchain_time / manual_time
            print(f"⚡ PERFORMANCE: Manual is {speedup:.1f}x faster than LangChain")
            print(f"   Manual: {manual_time:.3f}s vs LangChain: {langchain_time:.3f}s")
        else:
            speedup = manual_time / langchain_time
            print(f"⚡ PERFORMANCE: LangChain is {speedup:.1f}x faster than Manual")
            print(f"   LangChain: {langchain_time:.3f}s vs Manual: {manual_time:.3f}s")
        
        print()
        
        # Complexity analysis
        high_complexity_cases = [i for i, tc in enumerate(self.test_cases) if tc['complexity'] == 'high']
        if high_complexity_cases:
            lc_high_accuracy = np.mean([self.metrics['langchain']['accuracy'][i] for i in high_complexity_cases]) * 100
            manual_high_accuracy = np.mean([self.metrics['manual']['accuracy'][i] for i in high_complexity_cases]) * 100
            
            print(f"🧩 COMPLEXITY HANDLING:")
            print(f"   High complexity cases: LangChain {lc_high_accuracy:.1f}% vs Manual {manual_high_accuracy:.1f}%")
            
            if lc_high_accuracy > manual_high_accuracy:
                print(f"   ✅ LangChain better at handling complex, conflicting reviews")
            else:
                print(f"   ⚠️  Manual performs better even on complex cases")
        
        print()
        
        # Discussion advantage
        avg_discussions = np.mean(self.metrics['langchain']['discussion_rounds'])
        cases_with_discussion = sum(1 for d in self.metrics['langchain']['discussion_rounds'] if d > 0)
        
        print(f"💬 DISCUSSION ANALYSIS:")
        print(f"   Average discussion rounds: {avg_discussions:.1f}")
        print(f"   Cases requiring discussion: {cases_with_discussion}/{len(self.test_cases)}")
        
        if cases_with_discussion > 0:
            print(f"   ✅ LangChain successfully handles agent disagreements through discussion")
        else:
            print(f"   ⚠️  No agent disagreements detected - may need threshold adjustment")
        
        print()
        print(f"🎯 FINAL RECOMMENDATION:")
        
        if langchain_accuracy > manual_accuracy + 5:  # 5% threshold
            print(f"   ✅ Use LangChain workflow for better accuracy, especially on complex reviews")
        elif manual_time < langchain_time / 2:  # 2x speed difference
            print(f"   ⚡ Use Manual workflow for faster processing when accuracy is sufficient")
        else:
            print(f"   🤔 Both workflows show similar performance - choose based on specific needs")
            
        print(f"   📊 Consider hybrid approach: Manual for simple cases, LangChain for complex ones")


def main():
    """Main execution function"""
    
    # Check dependencies
    try:
        import pandas as pd
        import tabulate
        import numpy as np
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install: pip install pandas tabulate numpy")
        return
    
    print("🚀 VISUAL WORKFLOW COMPARISON TOOL")
    print("=" * 60)
    
    # Initialize comparator
    comparator = VisualWorkflowComparator()
    
    # Run comprehensive evaluation
    comparator.run_comprehensive_evaluation()
    
    print("\n✅ EVALUATION COMPLETE")
    print("Check the detailed report above for comprehensive analysis.")


if __name__ == "__main__":
    main() 