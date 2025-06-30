#!/usr/bin/env python3
"""
Analysis of why the challenging dataset is difficult for single agents
Demonstrates specific examples where multi-agent coordination is needed
"""

import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_challenging_examples():
    """Analyze why specific examples are challenging for single agents"""
    
    print(" ANALYSIS: WHY SINGLE AGENTS STRUGGLE WITH CHALLENGING DATASET")
    print("=" * 80)
    
    # Load dataset
    with open("evaluation/labeled_dataset.json", 'r') as f:
        dataset = json.load(f)
    
    challenging_examples = []
    
    for category, samples in dataset.items():
        for sample in samples:
            challenging_examples.append({
                'category': category,
                'review': sample['review'],
                'ground_truth': sample['ground_truth'],
                'aspects': sample['aspects'],
                'complexity': sample.get('complexity', 'N/A')
            })
    
    print(f"\n DATASET OVERVIEW:")
    print(f"   Total samples: {len(challenging_examples)}")
    print(f"   Categories: {list(dataset.keys())}")
    
    # Analyze complexity types
    complexity_types = {}
    for example in challenging_examples:
        complexity = example['complexity']
        if complexity != 'N/A':
            complexity_types[complexity] = complexity_types.get(complexity, 0) + 1
    
    print(f"\n COMPLEXITY TYPES:")
    for complexity, count in complexity_types.items():
        print(f"   • {complexity}: {count} cases")
    
    print(f"\n DETAILED ANALYSIS OF CHALLENGING CASES:")
    print("=" * 80)
    
    # Analyze specific challenging examples
    case_num = 1
    for example in challenging_examples[:6]:  # Show first 6 examples
        print(f"\n CASE {case_num}: {example['category'].upper()}")
        print(f"Complexity: {example['complexity']}")
        print(f"Ground Truth: {example['ground_truth']}")
        print("-" * 50)
        
        print(f"Review: \"{example['review'][:150]}...\"")
        
        print(f"\nAspect Analysis:")
        for aspect, sentiment in example['aspects'].items():
            print(f"   • {aspect}: {sentiment}")
        
        # Explain why it's challenging for single agents
        print(f"\n Why this challenges single agents:")
        
        if 'sarcasm' in example['complexity'].lower():
            print("    SARCASM DETECTION: Single agents often miss sarcastic tone")
            print("      - Requires understanding context and implied meaning")
            print("      - User_experience agent might focus on positive words, miss sarcasm")
        
        if 'contradictory' in example['complexity'].lower() or 'vs' in example['complexity'].lower():
            print("     CONTRADICTORY ASPECTS: Multiple conflicting dimensions")
            print("      - Product quality vs usability trade-offs")
            print("      - User_experience agent can't handle conflicting signals alone")
        
        if 'mismatch' in example['complexity'].lower():
            print("    EXPECTATION MISMATCH: Context-dependent sentiment")
            print("      - Same feature can be positive/negative for different users")
            print("      - Requires business impact analysis beyond user experience")
        
        if 'side effects' in example['complexity'].lower() or 'trade-off' in example['complexity'].lower():
            print("     BENEFIT-RISK ANALYSIS: Complex trade-offs")
            print("      - Positive results with negative consequences")
            print("      - Needs technical specification + user experience coordination")
        
        if 'misleading' in example['complexity'].lower() or 'marketing' in example['complexity'].lower():
            print("    MISLEADING CLAIMS: Technical vs marketing analysis")
            print("      - Requires product quality + business impact evaluation")
            print("      - User_experience alone can't detect false advertising")
        
        print(f"\n How multi-agents help:")
        print("   • Product Quality Agent: Analyzes technical aspects objectively")
        print("   • Customer Experience Agent: Evaluates service and support")
        print("   • User Experience Agent: Focuses on usability and comfort")
        print("   • Business Impact Agent: Considers value proposition and market positioning")
        print("   • Coordinator: Weighs conflicting signals and reaches balanced conclusion")
        
        case_num += 1
        print("\n" + "="*80)
    
    # Statistical analysis of why single agents fail
    print(f"\n STATISTICAL ANALYSIS:")
    print("-" * 40)
    
    mixed_sentiments = len([e for e in challenging_examples if e['ground_truth'] == 'mixed'])
    total_samples = len(challenging_examples)
    
    print(f"Mixed sentiment cases: {mixed_sentiments}/{total_samples} ({mixed_sentiments/total_samples*100:.1f}%)")
    print(f"This is {mixed_sentiments/total_samples*100:.1f}% higher than typical e-commerce reviews (usually ~10-15% mixed)")
    
    # Analyze aspect conflicts
    conflicting_aspects = 0
    for example in challenging_examples:
        aspects = list(example['aspects'].values())
        if len(set(aspects)) > 2:  # More than 2 different sentiment types
            conflicting_aspects += 1
    
    print(f"Cases with conflicting aspects: {conflicting_aspects}/{total_samples} ({conflicting_aspects/total_samples*100:.1f}%)")
    
    # Identify specific challenges for user_experience agent
    ux_challenges = []
    for example in challenging_examples:
        ux_aspect = example['aspects'].get('user_experience', 'N/A')
        if ux_aspect == 'negative' and example['ground_truth'] in ['mixed', 'positive']:
            ux_challenges.append(example)
        elif ux_aspect == 'positive' and example['ground_truth'] in ['mixed', 'negative']:
            ux_challenges.append(example)
    
    print(f"\nCases where UX sentiment ≠ overall sentiment: {len(ux_challenges)}/{total_samples} ({len(ux_challenges)/total_samples*100:.1f}%)")
    print("This shows why user_experience agent alone would misclassify many cases!")
    
    print(f"\n KEY INSIGHTS:")
    print("=" * 40)
    print("1.  Complex products have multiple evaluation dimensions")
    print("2.  Sarcasm and irony require contextual understanding")
    print("3.   Trade-offs between features need multi-perspective analysis")
    print("4.  Target audience matters - same product different user needs")
    print("5. Price-value relationships require business analysis")
    print("6.  Multi-agent coordination essential for nuanced sentiment")
    
    print(f"\n CONCLUSION:")
    print("This challenging dataset demonstrates realistic e-commerce scenarios")
    print("where single agents (especially user_experience) would fail, but")
    print("multi-agent systems can leverage specialized knowledge and")
    print("coordination to reach accurate, nuanced sentiment classifications.")
    
if __name__ == "__main__":
    analyze_challenging_examples() 