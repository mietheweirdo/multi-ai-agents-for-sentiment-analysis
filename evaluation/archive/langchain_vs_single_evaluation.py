#!/usr/bin/env python3
"""
LangChain vs Single Agent Evaluation Script
Compares Single Agent vs LangChain Multi-Agent performance with detailed metrics
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

class LangChainVsSingleEvaluator:
    """Evaluator comparing LangChain system vs Single Agent"""
    
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
            test_case = sample.get('test_case', 'unknown')
            
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
                    'test_case': test_case
                })
                
                status = "✅" if is_correct else "❌"
                print(f"  {status} {ground_truth} → {predicted} (conf: {confidence:.3f}) | {test_case}")
                
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': 'error',
                    'confidence': 0.0,
                    'reasoning': f'Error: {str(e)}',
                    'correct': False,
                    'test_case': test_case
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
            max_discussion_rounds=2  # Allow more discussion for better analysis
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
            test_case = sample.get('test_case', 'unknown')
            
            try:
                # Analyze with LangGraph multi-agent system
                analysis_result = coordinator.run_analysis(review)
                
                # Extract data from result
                master_analysis = analysis_result.get('master_analysis', {})
                predicted = master_analysis.get('sentiment', 'neutral')
                confidence = master_analysis.get('confidence', 0.5)
                master_reasoning = master_analysis.get('reasoning', 'No reasoning provided')
                
                # Count discussion rounds
                discussion_messages = analysis_result.get('discussion_messages', [])
                rounds = len(discussion_messages)
                discussion_rounds.append(rounds)
                
                is_correct = ground_truth == predicted
                if is_correct:
                    correct += 1
                total += 1
                confidence_scores.append(confidence)
                
                # Get agent analyses for detailed view
                agent_analyses = analysis_result.get('agent_analyses', {})
                agent_summary = {}
                for agent_type, analysis in agent_analyses.items():
                    agent_summary[agent_type] = {
                        'sentiment': analysis.get('sentiment', 'unknown'),
                        'confidence': analysis.get('confidence', 0.0)
                    }
                
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': predicted,
                    'confidence': confidence,
                    'master_reasoning': master_reasoning[:300] + "..." if len(master_reasoning) > 300 else master_reasoning,
                    'discussion_rounds': rounds,
                    'agent_analyses': agent_summary,
                    'correct': is_correct,
                    'test_case': test_case
                })
                
                status = "✅" if is_correct else "❌"
                print(f"  {status} {ground_truth} → {predicted} (conf: {confidence:.3f}, rounds: {rounds}) | {test_case}")
                
            except Exception as e:
                print(f"  ⚠️ Error: {e}")
                results.append({
                    'review': review[:150] + "..." if len(review) > 150 else review,
                    'ground_truth': ground_truth,
                    'predicted': 'error',
                    'confidence': 0.0,
                    'master_reasoning': f'Error: {str(e)}',
                    'discussion_rounds': 0,
                    'agent_analyses': {},
                    'correct': False,
                    'test_case': test_case
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
        """Compare Single Agent vs LangChain approaches"""
        print(f"\n🔍 So sánh Single Agent vs LangChain cho {category.upper()}")
        print("=" * 70)
        
        # Run evaluations
        single_result = self.evaluate_single_agent(category)
        langchain_result = self.evaluate_langchain_system(category)
        
        # Calculate improvements and differences
        accuracy_diff = langchain_result['accuracy'] - single_result['accuracy']
        accuracy_improvement_percent = (accuracy_diff / single_result['accuracy'] * 100) if single_result['accuracy'] > 0 else 0
        confidence_diff = langchain_result['avg_confidence'] - single_result['avg_confidence']
        time_ratio = langchain_result['processing_time'] / single_result['processing_time'] if single_result['processing_time'] > 0 else 1
        
        # Print detailed comparison
        print(f"\n📊 KẾT QUẢ CHI TIẾT")
        print("=" * 50)
        
        print(f"🤖 Single Agent:")
        print(f"  • Độ chính xác: {single_result['accuracy']:.1%} ({single_result['correct']}/{single_result['total']})")
        print(f"  • Confidence trung bình: {single_result['avg_confidence']:.3f}")
        print(f"  • Confidence cao nhất: {single_result['max_confidence']:.3f}")
        print(f"  • Thời gian xử lý: {single_result['processing_time']:.1f}s")
        
        print(f"\n🧠 LangChain Multi-Agent:")
        print(f"  • Độ chính xác: {langchain_result['accuracy']:.1%} ({langchain_result['correct']}/{langchain_result['total']})")
        print(f"  • Confidence trung bình: {langchain_result['avg_confidence']:.3f}")
        print(f"  • Confidence cao nhất: {langchain_result['max_confidence']:.3f}")
        print(f"  • Thời gian xử lý: {langchain_result['processing_time']:.1f}s")
        print(f"  • Số vòng thảo luận TB: {langchain_result['avg_discussion_rounds']:.1f}")
        print(f"  • Vòng thảo luận tối đa: {langchain_result['max_discussion_rounds']}")
        
        print(f"\n📈 SO SÁNH:")
        print(f"  • Cải thiện độ chính xác: {accuracy_diff:+.1%} ({accuracy_improvement_percent:+.1f}%)")
        print(f"  • Cải thiện confidence: {confidence_diff:+.3f}")
        print(f"  • Tỉ lệ thời gian: {time_ratio:.1f}x")
        
        # Analyze advantages
        print(f"\n💡 PHÂN TÍCH:")
        if accuracy_diff > 0:
            print(f"  ✅ LangChain có độ chính xác cao hơn {accuracy_diff:.1%}")
        elif accuracy_diff < 0:
            print(f"  ✅ Single Agent có độ chính xác cao hơn {abs(accuracy_diff):.1%}")
        else:
            print(f"  🤝 Cả hai có độ chính xác tương đương")
            
        if confidence_diff > 0:
            print(f"  ✅ LangChain có confidence cao hơn {confidence_diff:.3f}")
        elif confidence_diff < 0:
            print(f"  ✅ Single Agent có confidence cao hơn {abs(confidence_diff):.3f}")
        else:
            print(f"  🤝 Cả hai có confidence tương đương")
            
        if time_ratio > 1.5:
            print(f"  ⏱️ Single Agent nhanh hơn {time_ratio:.1f}x lần")
        elif time_ratio < 0.75:
            print(f"  ⏱️ LangChain nhanh hơn {1/time_ratio:.1f}x lần")
        else:
            print(f"  ⏱️ Thời gian xử lý tương đương")
            
        if langchain_result['avg_discussion_rounds'] > 0.5:
            print(f"  🗣️ LangChain có khả năng thảo luận và phân tích sâu")
        
        return {
            'category': category,
            'single_agent': single_result,
            'langchain_system': langchain_result,
            'comparison': {
                'accuracy_difference': accuracy_diff,
                'accuracy_improvement_percent': accuracy_improvement_percent,
                'confidence_difference': confidence_diff,
                'time_ratio': time_ratio,
                'langchain_has_discussions': langchain_result['avg_discussion_rounds'] > 0
            }
        }
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all categories"""
        print("🚀 Đánh giá toàn diện: LangChain vs Single Agent")
        print("=" * 70)
        
        results = {}
        categories = list(self.dataset.keys())
        
        for category in categories:
            results[category] = self.compare_approaches(category)
        
        # Overall summary
        print(f"\n🎯 TỔNG KẾT TOÀN BỘ")
        print("=" * 50)
        
        # Calculate overall metrics
        total_single_correct = sum(results[cat]['single_agent']['correct'] for cat in categories)
        total_single_total = sum(results[cat]['single_agent']['total'] for cat in categories)
        total_langchain_correct = sum(results[cat]['langchain_system']['correct'] for cat in categories)
        total_langchain_total = sum(results[cat]['langchain_system']['total'] for cat in categories)
        
        overall_single_accuracy = total_single_correct / total_single_total if total_single_total > 0 else 0
        overall_langchain_accuracy = total_langchain_correct / total_langchain_total if total_langchain_total > 0 else 0
        overall_accuracy_improvement = overall_langchain_accuracy - overall_single_accuracy
        
        # Calculate overall confidence
        single_confidences = []
        langchain_confidences = []
        total_processing_time_single = 0
        total_processing_time_langchain = 0
        total_discussions = 0
        
        for cat in categories:
            single_confidences.extend([r['confidence'] for r in results[cat]['single_agent']['results']])
            langchain_confidences.extend([r['confidence'] for r in results[cat]['langchain_system']['results']])
            total_processing_time_single += results[cat]['single_agent']['processing_time']
            total_processing_time_langchain += results[cat]['langchain_system']['processing_time']
            total_discussions += results[cat]['langchain_system']['avg_discussion_rounds']
        
        overall_single_confidence = sum(single_confidences) / len(single_confidences) if single_confidences else 0
        overall_langchain_confidence = sum(langchain_confidences) / len(langchain_confidences) if langchain_confidences else 0
        overall_confidence_improvement = overall_langchain_confidence - overall_single_confidence
        overall_time_ratio = total_processing_time_langchain / total_processing_time_single if total_processing_time_single > 0 else 1
        
        print(f"📊 Single Agent tổng thể:")
        print(f"  • Độ chính xác: {overall_single_accuracy:.1%} ({total_single_correct}/{total_single_total})")
        print(f"  • Confidence TB: {overall_single_confidence:.3f}")
        print(f"  • Tổng thời gian: {total_processing_time_single:.1f}s")
        
        print(f"\n🧠 LangChain tổng thể:")
        print(f"  • Độ chính xác: {overall_langchain_accuracy:.1%} ({total_langchain_correct}/{total_langchain_total})")
        print(f"  • Confidence TB: {overall_langchain_confidence:.3f}")
        print(f"  • Tổng thời gian: {total_processing_time_langchain:.1f}s")
        print(f"  • TB thảo luận/category: {total_discussions/len(categories):.1f} vòng")
        
        print(f"\n🏆 KẾT LUẬN:")
        print(f"  • Cải thiện độ chính xác: {overall_accuracy_improvement:+.1%}")
        print(f"  • Cải thiện confidence: {overall_confidence_improvement:+.3f}")
        print(f"  • Tỉ lệ thời gian: {overall_time_ratio:.1f}x")
        
        # Determine winner
        if overall_accuracy_improvement > 0.01:  # > 1%
            print(f"  🥇 LangChain thắng về độ chính xác")
        elif overall_accuracy_improvement < -0.01:  # < -1%
            print(f"  🥇 Single Agent thắng về độ chính xác")
        else:
            if overall_confidence_improvement > 0.02:  # > 0.02 confidence
                print(f"  🥇 LangChain thắng về confidence và reasoning")
            elif overall_confidence_improvement < -0.02:
                print(f"  🥇 Single Agent thắng về confidence")
            else:
                print(f"  🤝 Hiệu suất tương đương, LangChain có reasoning tốt hơn")
        
        # Save results
        results['overall_summary'] = {
            'single_agent': {
                'accuracy': overall_single_accuracy,
                'confidence': overall_single_confidence,
                'total_time': total_processing_time_single,
                'total_correct': total_single_correct,
                'total_samples': total_single_total
            },
            'langchain_system': {
                'accuracy': overall_langchain_accuracy,
                'confidence': overall_langchain_confidence,
                'total_time': total_processing_time_langchain,
                'total_correct': total_langchain_correct,
                'total_samples': total_langchain_total,
                'avg_discussions_per_category': total_discussions/len(categories)
            },
            'improvements': {
                'accuracy': overall_accuracy_improvement,
                'confidence': overall_confidence_improvement,
                'time_ratio': overall_time_ratio
            }
        }
        
        # Save to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f'evaluation/langchain_vs_single_results_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Kết quả đã lưu vào: {filename}")
        
        return results

def main():
    """Main function"""
    print("🤖 vs 🧠 LangChain vs Single Agent Evaluation")
    print("=" * 70)
    
    try:
        evaluator = LangChainVsSingleEvaluator()
        results = evaluator.run_full_evaluation()
        
        print("\n✅ Đánh giá hoàn thành thành công!")
        print("🎉 Cảm ơn bạn đã sử dụng hệ thống đánh giá!")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 