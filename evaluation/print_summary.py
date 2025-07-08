#!/usr/bin/env python3
"""
Evaluation Results Summary Script
Reads all evaluation result files and provides comprehensive overview
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class EvaluationSummary:
    """Summarizes all evaluation results"""
    
    def __init__(self, results_dir: str = "evaluation/results"):
        """Initialize summary with results directory"""
        self.results_dir = results_dir
        self.result_files = self._find_result_files()
    
    def _find_result_files(self) -> List[str]:
        """Find all JSON result files"""
        if not os.path.exists(self.results_dir):
            return []
        
        pattern = os.path.join(self.results_dir, "*.json")
        files = glob.glob(pattern)
        return sorted(files, key=os.path.getmtime, reverse=True)  # Most recent first
    
    def _load_result_file(self, file_path: str) -> Dict[str, Any]:
        """Load a single result file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading {file_path}: {e}")
            return {}
    
    def _extract_comparison_type(self, file_path: str) -> str:
        """Extract comparison type from filename"""
        filename = os.path.basename(file_path)
        if "single_vs_langchain" in filename:
            return "Single vs LangChain"
        elif "manual_vs_langchain" in filename:
            return "Manual vs LangChain"
        elif "workflow_comparison" in filename:
            return "Workflow Comparison"
        else:
            return "Unknown Comparison"
    
    def _format_file_info(self, file_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format file information for display"""
        metadata = data.get('test_metadata', {})
        filename = os.path.basename(file_path)
        
        # Extract date from filename or metadata
        file_date = "Unknown"
        if metadata.get('test_date'):
            try:
                date_obj = datetime.fromisoformat(metadata['test_date'].replace('Z', '+00:00'))
                file_date = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                file_date = metadata['test_date'][:16]
        
        return {
            'filename': filename,
            'comparison_type': self._extract_comparison_type(file_path),
            'workflows_compared': metadata.get('workflows_compared', ['unknown']),
            'test_date': file_date,
            'total_cases': metadata.get('total_cases', 0),
            'categories': len(data.get('results', {})),
            'file_path': file_path
        }
    
    def print_available_results(self):
        """Print overview of all available result files"""
        print("📊 EVALUATION SUMMARY")
        print("=" * 50)
        
        if not self.result_files:
            print("❌ No evaluation results found in evaluation/results/")
            print("Run evaluation scripts first:")
            print("  python evaluation/compare_single_vs_langchain.py")
            print("  python evaluation/compare_manual_vs_langchain.py")
            return
        
        print(f"🔍 Found {len(self.result_files)} evaluation result files:\n")
        
        # Group by comparison type
        comparison_groups = {}
        for file_path in self.result_files:
            data = self._load_result_file(file_path)
            if data:
                info = self._format_file_info(file_path, data)
                comp_type = info['comparison_type']
                if comp_type not in comparison_groups:
                    comparison_groups[comp_type] = []
                comparison_groups[comp_type].append(info)
        
        # Print grouped results
        for comp_type, files in comparison_groups.items():
            print(f"📁 {comp_type}:")
            for info in files:
                workflows = " vs ".join(info['workflows_compared'])
                print(f"  • {info['filename']}")
                print(f"    Date: {info['test_date']} | Cases: {info['total_cases']} | Categories: {info['categories']}")
                print(f"    Workflows: {workflows}")
            print()
    
    def print_latest_performance(self):
        """Print performance summary from latest results"""
        print("📈 LATEST PERFORMANCE COMPARISON")
        print("=" * 50)
        
        if not self.result_files:
            print("❌ No results available")
            return
        
        # Find latest file for each comparison type
        latest_results = {}
        for file_path in self.result_files:
            data = self._load_result_file(file_path)
            if data:
                comp_type = self._extract_comparison_type(file_path)
                if comp_type not in latest_results:
                    latest_results[comp_type] = (file_path, data)
        
        # Print comparison table header
        print(f"{'Comparison':<20} {'Winner':<15} {'Accuracy':<20} {'Avg Time':<15} {'Discussion':<12}")
        print("-" * 85)
        
        summary_data = []
        
        for comp_type, (file_path, data) in latest_results.items():
            results = data.get('results', {})
            
            if not results:
                continue
            
            # Calculate overall statistics
            total_accuracy_1 = 0
            total_accuracy_2 = 0
            total_time_1 = 0
            total_time_2 = 0
            total_discussions = 0
            categories = 0
            
            workflow_names = []
            winner_count = {0: 0, 1: 0}  # Track wins for each workflow
            
            for category, category_data in results.items():
                if not category_data:
                    continue
                
                categories += 1
                
                # Extract workflow names from first category
                if not workflow_names:
                    if 'single_agent' in category_data:
                        workflow_names = ['Single Agent', 'LangChain']
                        wf1_data = category_data['single_agent']
                        wf2_data = category_data.get('langchain_system', category_data.get('langchain', {}))
                    elif 'manual_workflow' in category_data:
                        workflow_names = ['Manual', 'LangChain']
                        wf1_data = category_data['manual_workflow']
                        wf2_data = category_data['langchain_system']
                    else:
                        continue
                else:
                    # Get workflow data based on established names
                    if workflow_names[0] == 'Single Agent':
                        wf1_data = category_data['single_agent']
                        wf2_data = category_data.get('langchain_system', category_data.get('langchain', {}))
                    else:
                        wf1_data = category_data['manual_workflow']
                        wf2_data = category_data['langchain_system']
                
                # Accumulate statistics
                total_accuracy_1 += wf1_data.get('accuracy', 0)
                total_accuracy_2 += wf2_data.get('accuracy', 0)
                total_time_1 += wf1_data.get('processing_time', 0)
                total_time_2 += wf2_data.get('processing_time', 0)
                total_discussions += wf2_data.get('avg_discussion_rounds', 0)
                
                # Determine category winner
                if wf2_data.get('accuracy', 0) > wf1_data.get('accuracy', 0):
                    winner_count[1] += 1
                elif wf1_data.get('accuracy', 0) > wf2_data.get('accuracy', 0):
                    winner_count[0] += 1
            
            if categories == 0:
                continue
            
            # Calculate averages
            avg_accuracy_1 = total_accuracy_1 / categories
            avg_accuracy_2 = total_accuracy_2 / categories
            avg_time_1 = total_time_1 / categories
            avg_time_2 = total_time_2 / categories
            avg_discussions = total_discussions / categories
            
            # Determine overall winner
            if winner_count[1] > winner_count[0]:
                winner = workflow_names[1]
            elif winner_count[0] > winner_count[1]:
                winner = workflow_names[0]
            else:
                winner = "Tie"
            
            # Format output
            accuracy_str = f"{avg_accuracy_1:.1%} vs {avg_accuracy_2:.1%}"
            time_str = f"{avg_time_1:.1f}s vs {avg_time_2:.1f}s"
            discussion_str = f"{avg_discussions:.1f} rounds" if avg_discussions > 0 else "None"
            
            print(f"{comp_type:<20} {winner:<15} {accuracy_str:<20} {time_str:<15} {discussion_str:<12}")
            
            summary_data.append({
                'comparison': comp_type,
                'winner': winner,
                'workflows': workflow_names,
                'accuracy_1': avg_accuracy_1,
                'accuracy_2': avg_accuracy_2,
                'time_1': avg_time_1,
                'time_2': avg_time_2,
                'discussions': avg_discussions,
                'categories': categories
            })
        
        return summary_data
    
    def print_key_findings(self, summary_data: List[Dict[str, Any]]):
        """Print key findings from all evaluations"""
        print("\n🎯 KEY FINDINGS")
        print("=" * 30)
        
        if not summary_data:
            print("❌ No summary data available")
            return
        
        # Track LangChain performance
        langchain_wins = 0
        total_comparisons = len(summary_data)
        accuracy_improvements = []
        time_overheads = []
        discussion_capabilities = []
        
        for data in summary_data:
            # Check if LangChain won
            if "LangChain" in data['winner']:
                langchain_wins += 1
            
            # Calculate improvements (assuming LangChain is always second)
            accuracy_improvement = data['accuracy_2'] - data['accuracy_1']
            accuracy_improvements.append(accuracy_improvement)
            
            # Calculate time overhead
            if data['time_1'] > 0:
                time_ratio = data['time_2'] / data['time_1']
                time_overheads.append(time_ratio)
            
            # Track discussion capability
            if data['discussions'] > 0:
                discussion_capabilities.append(data['discussions'])
        
        # Print findings
        print(f"• LangChain wins: {langchain_wins}/{total_comparisons} comparisons ({langchain_wins/total_comparisons:.1%})")
        
        if accuracy_improvements:
            avg_acc_improvement = sum(accuracy_improvements) / len(accuracy_improvements)
            print(f"• Average accuracy improvement: {avg_acc_improvement:+.1%}")
        
        if time_overheads:
            avg_time_overhead = sum(time_overheads) / len(time_overheads)
            print(f"• Average time overhead: {avg_time_overhead:.1f}x")
        
        if discussion_capabilities:
            avg_discussions = sum(discussion_capabilities) / len(discussion_capabilities)
            print(f"• Average discussion rounds: {avg_discussions:.1f}")
            print(f"• Discussion capability: {len(discussion_capabilities)}/{total_comparisons} comparisons")
        
        # Strategic recommendations
        print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
        if langchain_wins > total_comparisons / 2:
            print(f"✅ LangChain dominates - use for production")
            if any(d > 0 for d in discussion_capabilities):
                print(f"✅ Discussion mechanism provides clear advantage for complex cases")
        else:
            print(f"⚠️  Mixed results - choose based on use case")
        
        if time_overheads and sum(time_overheads) / len(time_overheads) > 3:
            print(f"⚠️  Consider LangChain only for high-stakes analysis (significant time overhead)")
        else:
            print(f"✅ Time overhead acceptable for quality improvement")
    
    def print_detailed_breakdown(self):
        """Print detailed breakdown of latest results"""
        print("\n📋 DETAILED BREAKDOWN")
        print("=" * 40)
        
        if not self.result_files:
            print("❌ No results available")
            return
        
        # Show details from most recent file
        latest_file = self.result_files[0]
        data = self._load_result_file(latest_file)
        
        if not data:
            print("❌ Could not load latest results")
            return
        
        metadata = data.get('test_metadata', {})
        results = data.get('results', {})
        
        print(f"📁 File: {os.path.basename(latest_file)}")
        print(f"📅 Date: {metadata.get('test_date', 'Unknown')[:16]}")
        print(f"🔄 Workflows: {' vs '.join(metadata.get('workflows_compared', ['Unknown']))}")
        print(f"📊 Total Cases: {metadata.get('total_cases', 0)}")
        print()
        
        # Print category-by-category results
        for category, category_data in results.items():
            if not category_data:
                continue
            
            print(f"📦 {category.upper()}:")
            
            # Determine workflow names and data
            if 'single_agent' in category_data:
                wf1_name, wf2_name = "Single Agent", "LangChain"
                wf1_data = category_data['single_agent']
                wf2_data = category_data.get('langchain_system', category_data.get('langchain', {}))
            elif 'manual_workflow' in category_data:
                wf1_name, wf2_name = "Manual Workflow", "LangChain"
                wf1_data = category_data['manual_workflow']
                wf2_data = category_data['langchain_system']
            else:
                print("  ❌ Unknown workflow format")
                continue
            
            # Print comparison
            wf1_acc = wf1_data.get('accuracy', 0)
            wf2_acc = wf2_data.get('accuracy', 0)
            wf1_time = wf1_data.get('processing_time', 0)
            wf2_time = wf2_data.get('processing_time', 0)
            discussions = wf2_data.get('avg_discussion_rounds', 0)
            
            print(f"  {wf1_name}: {wf1_acc:.1%} accuracy, {wf1_time:.1f}s")
            print(f"  {wf2_name}: {wf2_acc:.1%} accuracy, {wf2_time:.1f}s, {discussions:.1f} discussions")
            
            # Winner
            if wf2_acc > wf1_acc:
                print(f"  🏆 Winner: {wf2_name} (+{wf2_acc-wf1_acc:.1%})")
            elif wf1_acc > wf2_acc:
                print(f"  🏆 Winner: {wf1_name} (+{wf1_acc-wf2_acc:.1%})")
            else:
                print(f"  🤝 Tie")
            print()
    
    def run_full_summary(self):
        """Run complete summary report"""
        self.print_available_results()
        summary_data = self.print_latest_performance()
        if summary_data:
            self.print_key_findings(summary_data)
            self.print_detailed_breakdown()

def main():
    """Main summary function"""
    summary = EvaluationSummary()
    summary.run_full_summary()

if __name__ == "__main__":
    main() 