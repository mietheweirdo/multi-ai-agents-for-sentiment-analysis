# 📖 User Guide - Multi-Agent Sentiment Analysis System

## 🎯 **Getting Started**

This guide will help you understand and use the Multi-Agent Sentiment Analysis System effectively. The system analyzes customer feedback using specialized AI agents that work together to provide comprehensive insights.

## 🏗️ **System Overview**

### What This System Does
- **Analyzes Customer Sentiment**: Determines if feedback is positive, negative, or mixed
- **Provides Business Insights**: Offers actionable recommendations for improvement
- **Multi-Perspective Analysis**: Uses 5 specialized departments for comprehensive review
- **Conflict Resolution**: Handles disagreements between different analytical perspectives

### Key Features
- **🔄 Real-time Analysis**: Process feedback in seconds
- **🤖 Multi-Agent Intelligence**: 5 specialized AI agents + master coordinator
- **📊 Business Recommendations**: Actionable advice for sellers/businesses
- **⚡ Multiple Interfaces**: Web UI, Python API, and A2A protocol

## 🚀 **Quick Start Guide**

### Method 1: Web Interface (Recommended for Beginners)

1. **Start the Application**:
   ```bash
   streamlit run app.py
   ```

2. **Open Your Browser**: Navigate to `http://localhost:8501`

3. **Enter Your Review**: Type or paste customer feedback

4. **Select Product Category**: Choose from electronics, fashion, books, etc.

5. **Click Analyze**: View comprehensive results with recommendations

### Method 2: Python Code (For Developers)

```python
from workflow_manager import analyze_review

# Simple analysis
result = analyze_review(
    review="This laptop has great performance but poor customer service",
    product_category="electronics"
)

# View results
print(f"Final Sentiment: {result['master_analysis']['sentiment']}")
print(f"Confidence: {result['master_analysis']['confidence']}")
print(f"Recommendation: {result['business_recommendations']['business_impact']}")
```

### Method 3: Interactive Demo

```bash
python demo_enhanced_system.py
```

Follow the menu options to explore different system capabilities.

## 🏢 **Understanding the 3-Layer Analysis**

### Layer 1: Department Agents (Specialized Analysis)

Each department analyzes the review from their unique perspective:

#### 🔧 Quality Department
- **Focus**: Product quality, durability, manufacturing
- **Example**: "The build quality is excellent" → Positive sentiment
- **Expertise**: Materials, craftsmanship, reliability

#### 🚚 Experience Department  
- **Focus**: Customer service, delivery, support
- **Example**: "Delivery was delayed" → Negative sentiment
- **Expertise**: Service quality, logistics, support responsiveness

#### 😊 User Experience Department
- **Focus**: Emotions, satisfaction, usability
- **Example**: "I love using this product" → Positive sentiment
- **Expertise**: User satisfaction, emotional response, ease of use

#### 💼 Business Department
- **Focus**: Market impact, value proposition
- **Example**: "Great value for money" → Positive sentiment
- **Expertise**: Pricing, market positioning, competitive advantage

#### ⚙️ Technical Department
- **Focus**: Features, specifications, performance
- **Example**: "Fast processor and good graphics" → Positive sentiment
- **Expertise**: Technical specifications, feature analysis, performance metrics

### Layer 2: Master Sentiment Analyst

- **Synthesizes** all department inputs
- **Resolves conflicts** when departments disagree
- **Provides final sentiment** with confidence score
- **Explains reasoning** behind the decision

### Layer 3: Business Advisor

- **Translates analysis** into actionable business advice
- **Prioritizes recommendations** by impact and feasibility
- **Focuses on seller benefits** and improvement strategies
- **Ready for chatbot integration** and customer communication

## 📊 **Interpreting Results**

### Basic Results Structure

```python
{
    "department_analyses": [
        {
            "agent_type": "quality",
            "sentiment": "positive",
            "confidence": 0.85,
            "reasoning": "Product quality mentioned positively",
            "key_factors": ["build quality", "durability"]
        }
        # ... 4 more departments
    ],
    "master_analysis": {
        "sentiment": "mixed",
        "confidence": 0.78,
        "reasoning": "Positive product aspects but negative service experience"
    },
    "business_recommendations": {
        "business_impact": "Focus on improving customer service training",
        "confidence": 0.82,
        "reasoning": "Service improvements could boost overall satisfaction"
    }
}
```

### Understanding Sentiment Scores

| Sentiment | Description | Action Needed |
|-----------|-------------|---------------|
| **Positive** | Customer satisfied | Maintain current standards |
| **Negative** | Customer dissatisfied | Immediate improvement needed |
| **Mixed** | Both positive and negative aspects | Targeted improvements |
| **Neutral** | No strong sentiment | Monitor for trends |

### Confidence Levels

| Range | Interpretation | Reliability |
|-------|----------------|-------------|
| **0.8-1.0** | High confidence | Very reliable |
| **0.6-0.8** | Moderate confidence | Generally reliable |
| **0.4-0.6** | Low confidence | Needs human review |
| **<0.4** | Very low confidence | Manual verification required |

## 🎛️ **Advanced Usage**

### Custom Configuration

```python
from workflow_manager import MultiAgentWorkflowManager

# Create custom workflow
workflow = MultiAgentWorkflowManager(
    product_category="fashion",
    department_types=["quality", "experience", "user_experience"],
    max_tokens_per_department=200,
    enable_discussion_rounds=True
)

# Analyze with custom settings
result = workflow.analyze_review("This dress is beautiful but shipping was slow")
```

### Batch Processing

```python
reviews = [
    "Great product, fast delivery!",
    "Poor quality, disappointed",
    "Amazing customer service, average product"
]

results = []
for review in reviews:
    result = analyze_review(review, product_category="electronics")
    results.append(result)

# Aggregate insights
positive_count = sum(1 for r in results if r['master_analysis']['sentiment'] == 'positive')
print(f"Positive reviews: {positive_count}/{len(reviews)}")
```

### Data Pipeline Integration

```python
from data_pipeline import collect_and_preprocess

# Process local data files
data = collect_and_preprocess(
    file_paths=["data/customer_reviews.json"],
    product_category="electronics",
    max_items_per_source=100
)

# Analyze all reviews
for item in data:
    result = analyze_review(
        review=item['review_text'],
        product_category=item['product_category']
    )
    print(f"Review: {item['review_text'][:50]}...")
    print(f"Sentiment: {result['master_analysis']['sentiment']}")
```

## 🔍 **Use Cases & Examples**

### E-commerce Businesses

**Problem**: Analyzing thousands of product reviews
**Solution**: Batch process reviews to identify improvement areas

```python
# Process e-commerce reviews
ecommerce_data = collect_and_preprocess(
    file_paths=["product_reviews.json"],
    product_category="electronics"
)

# Identify common issues
negative_reviews = []
for item in ecommerce_data:
    result = analyze_review(item['review_text'], "electronics")
    if result['master_analysis']['sentiment'] == 'negative':
        negative_reviews.append({
            'review': item['review_text'],
            'issues': result['business_recommendations']['business_impact']
        })
```

### Customer Support Teams

**Problem**: Prioritizing support tickets by sentiment urgency
**Solution**: Real-time sentiment analysis for ticket triage

```python
def prioritize_ticket(ticket_text):
    result = analyze_review(ticket_text, "general")
    
    if result['master_analysis']['confidence'] > 0.8:
        if result['master_analysis']['sentiment'] == 'negative':
            return "HIGH_PRIORITY"
        elif result['master_analysis']['sentiment'] == 'positive':
            return "LOW_PRIORITY"
    
    return "MEDIUM_PRIORITY"

# Example usage
ticket = "This product completely stopped working after one week!"
priority = prioritize_ticket(ticket)
print(f"Ticket priority: {priority}")
```

### Product Development Teams

**Problem**: Understanding which product features customers love/hate
**Solution**: Feature-specific sentiment analysis

```python
feature_reviews = [
    "The camera quality is amazing but battery life is poor",
    "Love the design but it's too expensive",
    "Great performance but gets very hot"
]

feature_analysis = {}
for review in feature_reviews:
    result = analyze_review(review, "electronics")
    
    # Extract department insights
    for dept in result['department_analyses']:
        if dept['agent_type'] not in feature_analysis:
            feature_analysis[dept['agent_type']] = []
        
        feature_analysis[dept['agent_type']].append({
            'sentiment': dept['sentiment'],
            'factors': dept['key_factors']
        })

print("Feature Analysis:", feature_analysis)
```

## 🔧 **Troubleshooting Common Issues**

### Issue 1: Low Confidence Scores

**Problem**: System returns low confidence scores
**Possible Causes**:
- Review text too short or ambiguous
- Mixed signals in the review
- Unusual language or slang

**Solutions**:
```python
# Check review length
if len(review_text) < 20:
    print("Review too short, consider getting more context")

# Use lower confidence threshold
if result['master_analysis']['confidence'] < 0.6:
    print("Low confidence - manual review recommended")
```

### Issue 2: Unexpected Sentiment Results

**Problem**: Sentiment doesn't match human interpretation
**Debugging**:
```python
# Check individual department analyses
for dept in result['department_analyses']:
    print(f"{dept['agent_type']}: {dept['sentiment']} ({dept['confidence']:.2f})")
    print(f"Reasoning: {dept['reasoning']}")

# Check for department disagreements
sentiments = [d['sentiment'] for d in result['department_analyses']]
if len(set(sentiments)) > 1:
    print("Department disagreement detected - check master analysis reasoning")
```

### Issue 3: Performance Issues

**Problem**: Analysis takes too long
**Solutions**:
```python
# Reduce token limits for faster processing
config = {
    "agents": {
        "max_tokens_per_agent": 100,
        "max_tokens_consensus": 300
    }
}

# Use simpler model
config["openai"]["model"] = "gpt-3.5-turbo"
```

## 📈 **Best Practices**

### 1. Choose Appropriate Product Categories
- **Electronics**: smartphones, laptops, gadgets
- **Fashion**: clothing, accessories, shoes
- **Books**: novels, textbooks, e-books
- **Home**: furniture, appliances, decorations
- **Beauty**: cosmetics, skincare, personal care

### 2. Optimize Review Quality
- **Minimum Length**: 20+ characters for meaningful analysis
- **Clear Language**: Avoid excessive slang or abbreviations
- **Context**: Include product-specific details when possible

### 3. Batch Processing Tips
```python
# Process in chunks to avoid rate limits
def batch_analyze(reviews, batch_size=10):
    results = []
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i+batch_size]
        batch_results = [analyze_review(r, "general") for r in batch]
        results.extend(batch_results)
        time.sleep(1)  # Rate limiting
    return results
```

### 4. Cost Optimization
```python
# Use cost-effective settings for large-scale processing
cost_optimized_config = {
    "openai": {
        "model": "gpt-3.5-turbo",
        "max_tokens": 300
    },
    "agents": {
        "max_tokens_per_agent": 75,
        "max_tokens_consensus": 200
    }
}
```

## 🎯 **Next Steps**

### For Business Users
1. **Start with Web Interface**: Use Streamlit app for initial testing
2. **Integrate with Your Data**: Use data pipeline to process your review files
3. **Set Up Monitoring**: Regular sentiment analysis of new reviews
4. **Create Dashboards**: Use results to build business intelligence dashboards

### For Developers
1. **Explore A2A Protocol**: Set up agent-to-agent communication
2. **Custom Agents**: Develop specialized agents for your domain
3. **API Integration**: Integrate sentiment analysis into your applications
4. **Advanced Workflows**: Experiment with LangGraph for complex discussions

### For Researchers
1. **Evaluation Suite**: Use evaluation tools to measure performance
2. **Custom Prompts**: Modify agent prompts for your research needs
3. **Comparison Studies**: Compare different multi-agent approaches
4. **Dataset Creation**: Build domain-specific datasets for training

---

**🎊 Happy Analyzing! Your Multi-Agent Sentiment Analysis System is Ready to Provide Insights!**
