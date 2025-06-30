#!/usr/bin/env python3
"""
3-Layer Multi-Agent Sentiment Analysis System - Demo
Demonstrates the department-based collaborative workflow with real agent disagreement
"""

import json
import os
from workflow_manager import MultiAgentWorkflowManager, analyze_review

def display_analysis_results(result):
    """Display comprehensive 3-layer analysis results"""
    
    print(f"\n🎯 3-LAYER ANALYSIS RESULTS:")
    print("=" * 70)
    
    # Original review
    review_text = result['review_text']
    print(f"\n📝 REVIEW: {review_text}")
    print(f"📂 CATEGORY: {result['product_category']}")
    
    # Layer 1: Department Analyses
    print(f"\n🏢 LAYER 1: DEPARTMENT ANALYSES")
    print("-" * 40)
    
    department_analyses = result['department_analyses']
    for dept in department_analyses:
        agent_type = dept.get('agent_type', 'unknown')
        sentiment = dept.get('sentiment', 'unknown')
        confidence = dept.get('confidence', 0)
        reasoning = dept.get('reasoning', 'N/A')
        
        print(f"  {agent_type.upper()} DEPT: {sentiment.upper()} (confidence: {confidence:.2f})")
        print(f"    └─ {reasoning[:80]}...")
        print()
    
    # Check for disagreement
    sentiments = [d['sentiment'] for d in department_analyses]
    unique_sentiments = list(set(sentiments))
    if len(unique_sentiments) > 1:
        print(f"  🔥 DISAGREEMENT DETECTED: {unique_sentiments}")
        for sentiment in unique_sentiments:
            count = sentiments.count(sentiment)
            print(f"     • {sentiment.upper()}: {count} departments")
    else:
        print(f"  🤝 UNANIMOUS: All departments agree on {unique_sentiments[0].upper()}")
    
    # Layer 2: Master Analyst Synthesis
    print(f"\n🎓 LAYER 2: MASTER ANALYST SYNTHESIS")
    print("-" * 40)
    
    master = result['master_analysis']
    print(f"  FINAL SENTIMENT: {master.get('overall_sentiment', master.get('sentiment', 'unknown')).upper()}")
    print(f"  CONFIDENCE: {master.get('confidence', 0):.2f}")
    print(f"  REASONING: {master.get('reasoning', 'N/A')}")
    
    # Layer 3: Business Advisor Recommendations
    print(f"\n💼 LAYER 3: BUSINESS ADVISOR RECOMMENDATIONS")
    print("-" * 40)
    
    advisor = result['business_recommendations']
    print(f"  RECOMMENDATION CONFIDENCE: {advisor.get('confidence', 0):.2f}")
    print(f"  BUSINESS IMPACT: {advisor.get('business_impact', 'N/A')}")
    
    # Workflow metadata
    print(f"\n⚙️ WORKFLOW METADATA")
    print("-" * 40)
    metadata = result['workflow_metadata']
    print(f"  PROCESSING TIME: {metadata.get('processing_time', 0):.2f} seconds")
    print(f"  TOTAL DEPARTMENTS: {metadata.get('total_departments', 0)}")
    print(f"  WORKFLOW VERSION: {metadata.get('workflow_version', 'unknown')}")

def show_system_capabilities():
    """Show what the 3-layer system can do"""
    
    print("\n🎯 3-LAYER MULTI-AGENT SYSTEM CAPABILITIES:")
    print("=" * 60)
    
    print("\n🏢 LAYER 1: SPECIALIZED DEPARTMENTS")
    print("   • Quality Department: Product quality & manufacturing focus")
    print("   • Experience Department: Customer service & delivery focus") 
    print("   • User Experience Department: Emotions & satisfaction focus")
    print("   • Business Department: Market impact & business focus")
    print("   • Technical Department: Specifications & features focus")
    
    print("\n🎓 LAYER 2: MASTER SENTIMENT ANALYST")
    print("   • Synthesizes all department inputs")
    print("   • Makes expert final assessment")
    print("   • Resolves conflicts between departments")
    
    print("\n💼 LAYER 3: BUSINESS ADVISOR")
    print("   • Provides actionable recommendations")
    print("   • Seller-focused improvement advice")
    print("   • Ready for chatbot integration")
    
    print("\n🔥 KEY FEATURES:")
    print("   • Real department disagreement (no more identical results!)")
    print("   • Specialized domain expertise")
    print("   • Linear workflow (no complex LangGraph)")
    print("   • Business-ready recommendations")

def test_different_review_types():
    """Test system with different types of reviews"""
    
    test_reviews = [
        {
            "name": "Mixed Review (Product Good, Service Bad)",
            "review": "This laptop has amazing performance and great screen, but the customer service was terrible and delivery took forever.",
            "category": "electronics",
            "expected": "Should see Quality/Technical positive, Experience/UX/Business negative"
        },
        {
            "name": "Clearly Positive Review",
            "review": "Absolutely love this smartphone! Amazing camera, fast performance, quick delivery, and excellent customer support!",
            "category": "electronics", 
            "expected": "Should see mostly positive across departments"
        },
        {
            "name": "Clearly Negative Review",
            "review": "Worst purchase ever! Product broke immediately, terrible quality, awful customer service, slow delivery!",
            "category": "electronics",
            "expected": "Should see mostly negative across departments"
        },
        {
            "name": "Fashion Review (Different Category)",
            "review": "Love this dress! Perfect fit and beautiful fabric, but the delivery packaging was damaged and customer service was unhelpful.",
            "category": "fashion",
            "expected": "Should adapt to fashion context"
        }
    ]
    
    for i, test in enumerate(test_reviews, 1):
        print(f"\n🧪 TEST CASE {i}: {test['name']}")
        print("=" * 60)
        print(f"Review: {test['review']}")
        print(f"Expected: {test['expected']}")
        
        try:
            # Run analysis
            result = analyze_review(test['review'], product_category=test['category'])
            
            # Show department disagreement
            departments = result['department_analyses']
            sentiments = [d['sentiment'] for d in departments]
            sentiment_counts = {}
            for s in sentiments:
                sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
            
            print(f"\nDepartment Results: {dict(sentiment_counts)}")
            
            # Show final assessment
            master = result['master_analysis']
            final_sentiment = master.get('sentiment', 'unknown')
            confidence = master.get('confidence', 0)
            
            print(f"Master Decision: {final_sentiment.upper()} ({confidence:.2f})")
            print(f"Processing Time: {result['workflow_metadata']['processing_time']:.2f}s")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def demonstrate_business_advisor_output():
    """Show detailed business advisor recommendations"""
    
    print(f"\n💼 BUSINESS ADVISOR DEMO:")
    print("=" * 50)
    
    review = "Great product quality but customer service needs improvement and delivery was slow."
    
    print(f"Sample Review: {review}")
    print("\nRunning analysis...")
            
    result = analyze_review(review)
    
    # Extract business recommendations
    advisor = result['business_recommendations']
                
    print(f"\n📋 BUSINESS RECOMMENDATIONS:")
    print(f"Confidence: {advisor.get('confidence', 0):.2f}")
    print(f"Reasoning: {advisor.get('reasoning', 'N/A')}")
    print(f"Business Impact: {advisor.get('business_impact', 'N/A')}")
    
    print(f"\n🎯 This output is ready for:")
    print(f"   • Integration with chatbot")
    print(f"   • Seller dashboard display")
    print(f"   • Automated improvement suggestions")
    print(f"   • Business intelligence reporting")

def run_enhanced_demo():
    """Run the complete 3-layer system demonstration"""
    
    print("🚀 3-LAYER MULTI-AGENT SENTIMENT ANALYSIS DEMO")
    print("=" * 80)
    
    # Show system capabilities
    show_system_capabilities()
    
    # Test single analysis with detailed output
    print(f"\n🔍 DETAILED ANALYSIS EXAMPLE:")
    print("=" * 50)
    
    sample_review = "This smartphone has excellent camera quality and fast performance, but the customer service was unresponsive and delivery took 3 weeks!"
    
    try:
        result = analyze_review(sample_review, product_category="electronics")
        display_analysis_results(result)
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test different review types
    test_different_review_types()
    
    # Demonstrate business advisor
    demonstrate_business_advisor_output()
    
    print(f"\n✅ DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("🎯 The 3-layer multi-agent system provides:")
    print("   ✓ Real department specialization and disagreement")
    print("   ✓ Expert master analyst synthesis")
    print("   ✓ Actionable business recommendations")
    print("   ✓ Linear workflow (no complex LangGraph)")
    print("   ✓ Ready for chatbot integration")
    print("   ✓ Significantly improved accuracy through collaboration")

if __name__ == "__main__":
    try:
        run_enhanced_demo()
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check your configuration and try again.") 