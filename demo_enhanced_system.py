#!/usr/bin/env python3
"""
3-Layer Multi-Agent Sentiment Analysis System - Demo
Demonstrates the department-based collaborative workflow with real agent disagreement
"""

import json
import os
from workflow_manager import MultiAgentWorkflowManager, analyze_review

# Import the new data pipeline
try:
    from data_pipeline import scrape_and_preprocess
    DYNAMIC_DATA_AVAILABLE = True
except ImportError:
    print("Warning: Data pipeline not available. Using static data only.")
    DYNAMIC_DATA_AVAILABLE = False

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
    
    # Interactive menu
    while True:
        print(f"\n📋 DEMO OPTIONS:")
        print("1. Static data analysis (original functionality)")
        print("2. Dynamic data analysis (real scraping)")
        print("3. Test different review types")
        print("4. Business advisor demo")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            run_static_demo()
        elif choice == "2":
            run_dynamic_demo()
        elif choice == "3":
            test_different_review_types()
        elif choice == "4":
            demonstrate_business_advisor_output()
        elif choice == "5":
            print("👋 Demo completed!")
            break
        else:
            print("❌ Invalid choice. Please select 1-5.")

def run_static_demo():
    """Run demo with static sample data"""
    print(f"\n🔍 STATIC DATA ANALYSIS EXAMPLE:")
    print("=" * 50)
    
    sample_review = "This smartphone has excellent camera quality and fast performance, but the customer service was unresponsive and delivery took 3 weeks!"
    
    try:
        result = analyze_review(sample_review, product_category="electronics")
        display_analysis_results(result)
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def run_dynamic_demo():
    """Run demo with real scraped data"""
    if not DYNAMIC_DATA_AVAILABLE:
        print("❌ Dynamic data not available. Please install data pipeline dependencies.")
        return
    
    print(f"\n🌐 DYNAMIC DATA ANALYSIS:")
    print("=" * 50)
    
    # Get user input
    keyword = input("Enter search keyword (e.g., 'smartphone', 'airpods'): ").strip()
    if not keyword:
        keyword = "smartphone"
    
    sources = input("Enter sources (youtube,tiki) or press Enter for tiki only: ").strip()
    if not sources:
        sources = ['tiki']  # Default to Tiki only for reliability
    else:
        sources = [s.strip() for s in sources.split(',') if s.strip() in ['youtube', 'tiki']]
    
    print(f"\n🔄 Scraping data for '{keyword}' from {sources}...")
    
    try:
        # Scrape real data (limit for demo)
        data = scrape_and_preprocess(
            keyword=keyword,
            sources=sources,
            max_items_per_source=5  # Limit for demo speed
        )
        
        if not data:
            print("❌ No data found. Please try a different keyword.")
            return
        
        print(f"✅ Found {len(data)} reviews. Analyzing first 3...")
        
        # Analyze first few items
        for i, item in enumerate(data[:3], 1):
            print(f"\n{'='*20} REVIEW {i} {'='*20}")
            
            try:
                result = analyze_review(
                    review=item['review_text'],
                    product_category=item['product_category']
                )
                display_analysis_results(result)
            except Exception as e:
                print(f"❌ Error analyzing review {i}: {e}")
                
        print(f"\n🎯 Dynamic data analysis completed!")
        
    except Exception as e:
        print(f"❌ Dynamic scraping failed: {e}")
        print("💡 Tip: Make sure your config.json has valid API keys.")

if __name__ == "__main__":
    try:
        run_enhanced_demo()
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check your configuration and try again.") 