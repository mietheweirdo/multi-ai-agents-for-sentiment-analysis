# visualize_langgraph.py
"""
Visualization and comparison tool for LangGraph vs Manual workflows
Shows the workflow graphs and execution paths
"""

import json
import os
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from agents.langgraph_coordinator import LangGraphCoordinator

def create_workflow_comparison_diagram():
    """Create a visual comparison of LangGraph vs Manual workflows"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
    fig.suptitle('LangGraph vs Manual Workflow Comparison', fontsize=16, fontweight='bold')
    
    # Manual Workflow (Left side)
    ax1.set_title('Manual Workflow', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 15)
    ax1.axis('off')
    
    # Manual workflow boxes
    manual_boxes = [
        (2, 13, "START", "lightgreen"),
        (2, 11, "Quality Agent", "lightblue"),
        (2, 9.5, "Experience Agent", "lightblue"),
        (2, 8, "UX Agent", "lightblue"),
        (2, 6.5, "Business Agent", "lightblue"),
        (2, 5, "Technical Agent", "lightblue"),
        (2, 3.5, "Master Analyst", "orange"),
        (2, 2, "Business Advisor", "yellow"),
        (2, 0.5, "END", "lightcoral")
    ]
    
    for x, y, text, color in manual_boxes:
        rect = patches.Rectangle((x-1, y-0.4), 2, 0.8, linewidth=1, 
                               edgecolor='black', facecolor=color)
        ax1.add_patch(rect)
        ax1.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Manual workflow arrows
    for i in range(len(manual_boxes)-1):
        y_start = manual_boxes[i][1] - 0.4
        y_end = manual_boxes[i+1][1] + 0.4
        ax1.arrow(2, y_start, 0, y_end - y_start - 0.1, 
                 head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Add workflow info
    ax1.text(5, 12, "Manual Workflow Features:", fontsize=12, fontweight='bold')
    ax1.text(5, 11.5, "• Sequential execution", fontsize=10)
    ax1.text(5, 11, "• No agent communication", fontsize=10)
    ax1.text(5, 10.5, "• Fixed linear pipeline", fontsize=10)
    ax1.text(5, 10, "• ~7 API calls", fontsize=10)
    ax1.text(5, 9.5, "• Fast & cost-efficient", fontsize=10)
    ax1.text(5, 9, "• Simple error handling", fontsize=10)
    
    # LangGraph Workflow (Right side)
    ax2.set_title('LangGraph Workflow with Discussion', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 12)
    ax2.set_ylim(0, 15)
    ax2.axis('off')
    
    # LangGraph workflow boxes
    langgraph_boxes = [
        (2, 13, "START", "lightgreen"),
        (2, 11, "Quality Agent", "lightblue"),
        (2, 9.5, "Experience Agent", "lightblue"),
        (2, 8, "UX Agent", "lightblue"),
        (2, 6.5, "Business Agent", "lightblue"),
        (2, 5, "Technical Agent", "lightblue"),
        (2, 3.5, "Check Consensus", "purple"),
        (6, 3.5, "Agent Discussion", "red"),
        (2, 2, "Master Synthesis", "orange"),
        (2, 0.5, "Business Advisor", "yellow"),
        (8, 0.5, "END", "lightcoral")
    ]
    
    for x, y, text, color in langgraph_boxes[:-1]:  # Exclude END for now
        rect = patches.Rectangle((x-1, y-0.4), 2, 0.8, linewidth=1, 
                               edgecolor='black', facecolor=color)
        ax2.add_patch(rect)
        ax2.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Add END box
    rect = patches.Rectangle((7, 0.1), 2, 0.8, linewidth=1, 
                           edgecolor='black', facecolor='lightcoral')
    ax2.add_patch(rect)
    ax2.text(8, 0.5, "END", ha='center', va='center', fontsize=10, fontweight='bold')
    
    # LangGraph arrows - sequential agents
    for i in range(5):  # Quality to Technical
        y_start = langgraph_boxes[i][1] - 0.4
        y_end = langgraph_boxes[i+1][1] + 0.4
        ax2.arrow(2, y_start, 0, y_end - y_start - 0.1, 
                 head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Technical to Check Consensus
    ax2.arrow(2, 4.6, 0, -0.7, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Conditional arrows from Check Consensus
    # To Discussion
    ax2.arrow(3, 3.5, 2, 0, head_width=0.1, head_length=0.1, fc='red', ec='red')
    ax2.text(4, 3.8, "Disagree", ha='center', fontsize=8, color='red')
    
    # To Master (consensus)
    ax2.arrow(2, 3.1, 0, -0.7, head_width=0.1, head_length=0.1, fc='green', ec='green')
    ax2.text(2.5, 2.8, "Agree", ha='center', fontsize=8, color='green')
    
    # Discussion back to Check Consensus
    ax2.arrow(5, 3.5, -2, 0, head_width=0.1, head_length=0.1, fc='red', ec='red', linestyle='--')
    ax2.text(4, 3.2, "Refine", ha='center', fontsize=8, color='red')
    
    # Master to Business Advisor
    ax2.arrow(2, 1.6, 0, -0.7, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Business Advisor to END
    ax2.arrow(3, 0.5, 4, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # Add workflow info
    ax2.text(9, 12, "LangGraph Features:", fontsize=12, fontweight='bold')
    ax2.text(9, 11.5, "• State-based workflow", fontsize=10)
    ax2.text(9, 11, "• Agent discussion", fontsize=10)
    ax2.text(9, 10.5, "• Consensus detection", fontsize=10)
    ax2.text(9, 10, "• Conditional execution", fontsize=10)
    ax2.text(9, 9.5, "• Dynamic API calls", fontsize=10)
    ax2.text(9, 9, "• Complex error handling", fontsize=10)
    ax2.text(9, 8.5, "• Workflow visualization", fontsize=10)
    
    plt.tight_layout()
    plt.savefig('workflow_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_execution_flow_diagram():
    """Create diagram showing different execution paths"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle('LangGraph Execution Paths', fontsize=16, fontweight='bold')
    
    # Consensus Path (Top)
    ax1.set_title('Execution Path 1: Consensus Reached (No Discussion)', fontsize=14)
    ax1.set_xlim(0, 12)
    ax1.set_ylim(0, 3)
    ax1.axis('off')
    
    consensus_steps = [
        (1, 1.5, "5 Agents\nAnalyze", "lightblue"),
        (3, 1.5, "Check\nConsensus", "purple"),
        (5, 1.5, "✓ Agree\n(≤60% disagree)", "lightgreen"),
        (7, 1.5, "Master\nSynthesis", "orange"),
        (9, 1.5, "Business\nRecommend", "yellow"),
        (11, 1.5, "END", "lightcoral")
    ]
    
    for x, y, text, color in consensus_steps:
        rect = patches.Rectangle((x-0.5, y-0.4), 1, 0.8, linewidth=1, 
                               edgecolor='black', facecolor=color)
        ax1.add_patch(rect)
        ax1.text(x, y, text, ha='center', va='center', fontsize=9, fontweight='bold')
    
    for i in range(len(consensus_steps)-1):
        ax1.arrow(consensus_steps[i][0]+0.5, consensus_steps[i][1], 1, 0, 
                 head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    ax1.text(6, 0.5, "API Calls: ~7 (similar to manual)", fontsize=10, color='green')
    
    # Discussion Path (Bottom)
    ax2.set_title('Execution Path 2: Discussion Needed (Disagreement)', fontsize=14)
    ax2.set_xlim(0, 16)
    ax2.set_ylim(0, 5)
    ax2.axis('off')
    
    discussion_steps = [
        (1, 3, "5 Agents\nAnalyze", "lightblue"),
        (3, 3, "Check\nConsensus", "purple"),
        (5, 3, "❌ Disagree\n(>60% disagree)", "lightcoral"),
        (7, 3, "Round 1\nDiscussion", "red"),
        (9, 3, "5 Agents\nRefine", "lightblue"),
        (11, 3, "Check Again", "purple"),
        (7, 1, "Round 2\nDiscussion", "red"),
        (13, 3, "Master\nSynthesis", "orange"),
        (15, 3, "Business\nRecommend", "yellow")
    ]
    
    for x, y, text, color in discussion_steps:
        rect = patches.Rectangle((x-0.5, y-0.4), 1, 0.8, linewidth=1, 
                               edgecolor='black', facecolor=color)
        ax2.add_patch(rect)
        ax2.text(x, y, text, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Main path arrows
    main_path = [(1, 3), (3, 3), (5, 3), (7, 3), (9, 3), (11, 3), (13, 3), (15, 3)]
    for i in range(len(main_path)-1):
        ax2.arrow(main_path[i][0]+0.5, main_path[i][1], 1, 0, 
                 head_width=0.1, head_length=0.1, fc='red', ec='red')
    
    # Discussion loop
    ax2.arrow(11, 2.6, -3.5, -1.2, head_width=0.1, head_length=0.1, fc='red', ec='red', linestyle='--')
    ax2.arrow(7.5, 1, 3, 1.6, head_width=0.1, head_length=0.1, fc='red', ec='red', linestyle='--')
    
    ax2.text(8, 0.2, "API Calls: ~17+ (2-3x more than manual)", fontsize=10, color='red')
    ax2.text(8, 4.5, "Discussion rounds can repeat up to max_discussion_rounds", fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig('execution_paths.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_cost_comparison():
    """Analyze and compare costs between workflows"""
    
    print("\n" + "💰" * 80)
    print("💰 COST ANALYSIS: LangGraph vs Manual Workflow")
    print("💰" * 80)
    
    # Assumptions for cost calculation
    cost_per_1k_tokens = 0.00015  # GPT-4o-mini input cost
    avg_tokens_per_call = 800    # Average tokens per API call
    
    print(f"\n📊 Cost Assumptions:")
    print(f"  • Model: GPT-4o-mini")
    print(f"  • Cost per 1K tokens: ${cost_per_1k_tokens}")
    print(f"  • Average tokens per call: {avg_tokens_per_call}")
    
    # Manual workflow cost
    manual_calls = 7  # 5 departments + 1 master + 1 advisor
    manual_cost = (manual_calls * avg_tokens_per_call * cost_per_1k_tokens) / 1000
    
    print(f"\n🔧 Manual Workflow:")
    print(f"  • API calls: {manual_calls}")
    print(f"  • Total tokens: ~{manual_calls * avg_tokens_per_call:,}")
    print(f"  • Cost per analysis: ${manual_cost:.6f}")
    print(f"  • Cost per 1000 analyses: ${manual_cost * 1000:.2f}")
    
    # LangGraph workflow costs (different scenarios)
    scenarios = [
        ("Consensus (no discussion)", 7, 0),
        ("1 discussion round", 12, 1),
        ("2 discussion rounds", 17, 2),
        ("Max discussion rounds", 22, 3)
    ]
    
    print(f"\n🔄 LangGraph Workflow:")
    for scenario, calls, rounds in scenarios:
        cost = (calls * avg_tokens_per_call * cost_per_1k_tokens) / 1000
        multiplier = cost / manual_cost if manual_cost > 0 else 0
        
        print(f"  • {scenario}:")
        print(f"    - API calls: {calls}")
        print(f"    - Discussion rounds: {rounds}")
        print(f"    - Cost: ${cost:.6f} ({multiplier:.1f}x manual)")
    
    # ROI Analysis
    print(f"\n📈 ROI Analysis:")
    print(f"  When is LangGraph worth the extra cost?")
    print(f"  • High-stakes decisions (extra accuracy matters)")
    print(f"  • Complex/contradictory reviews (need discussion)")
    print(f"  • Transparency needed (show agent reasoning)")
    print(f"  • Research/experimentation (understand agent behavior)")

def generate_workflow_summary():
    """Generate a summary comparing both workflows"""
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("\n" + "📋" * 80)
    print("📋 WORKFLOW SUMMARY & RECOMMENDATIONS")
    print("📋" * 80)
    
    comparison_data = {
        "Feature": [
            "Implementation Complexity", "Execution Speed", "API Call Cost", 
            "Agent Communication", "Consensus Detection", "Error Handling",
            "Workflow Visualization", "Extensibility", "Debugging Ease",
            "Production Readiness"
        ],
        "Manual Workflow": [
            "Simple", "Fast", "Low", "None", "None", "Basic",
            "None", "Moderate", "Easy", "High"
        ],
        "LangGraph Workflow": [
            "Complex", "Variable", "Variable", "Advanced", "Built-in", "Advanced",
            "Built-in", "High", "Moderate", "Moderate"
        ]
    }
    
    print(f"\n📊 Feature Comparison:")
    print(f"{'Feature':<25} {'Manual':<15} {'LangGraph':<15}")
    print(f"{'-'*60}")
    for i, feature in enumerate(comparison_data["Feature"]):
        manual = comparison_data["Manual Workflow"][i]
        langgraph = comparison_data["LangGraph Workflow"][i]
        print(f"{feature:<25} {manual:<15} {langgraph:<15}")
    
    print(f"\n✅ Use Manual Workflow When:")
    print(f"  • Need fast, cost-efficient analysis")
    print(f"  • Reviews are typically straightforward")
    print(f"  • Production system needs stability")
    print(f"  • Team wants simple maintenance")
    print(f"  • Budget is tight")
    
    print(f"\n🔄 Use LangGraph Workflow When:")
    print(f"  • Need explainable AI with agent reasoning")
    print(f"  • Handling complex/contradictory reviews")
    print(f"  • Research/experimentation is priority")
    print(f"  • Want to showcase advanced AI capabilities")
    print(f"  • Need workflow flexibility")
    
    print(f"\n💡 Hybrid Approach:")
    print(f"  • Use Manual for routine analysis")
    print(f"  • Use LangGraph for complex cases (trigger by disagreement)")
    print(f"  • Implement smart routing based on review complexity")

def main():
    """Run all visualization and analysis functions"""
    
    print("📊" * 80)
    print("📊 LANGGRAPH WORKFLOW VISUALIZATION & ANALYSIS")
    print("📊" * 80)
    
    try:
        print("\n🎨 Creating workflow comparison diagram...")
        create_workflow_comparison_diagram()
        
        print("\n🛤️ Creating execution flow diagram...")
        create_execution_flow_diagram()
        
        print("\n💰 Analyzing cost comparison...")
        analyze_cost_comparison()
        
        print("\n📋 Generating workflow summary...")
        generate_workflow_summary()
        
        print(f"\n✅ Visualization complete!")
        print(f"📁 Check for generated images:")
        print(f"  • workflow_comparison.png")
        print(f"  • execution_paths.png")
        
    except Exception as e:
        print(f"\n❌ Visualization failed: {e}")
        print(f"Make sure matplotlib is installed: pip install matplotlib")

if __name__ == "__main__":
    main() 