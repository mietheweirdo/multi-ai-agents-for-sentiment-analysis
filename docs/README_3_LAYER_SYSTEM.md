# 3-Layer Multi-Agent Sentiment Analysis System

A simplified, highly effective multi-agent system for sentiment analysis that achieves **real agent disagreement** and **collaborative synthesis**.

## 🏗️ System Architecture

### Layer 1: Specialized Department Agents
- **Quality Department**: Product quality & manufacturing focus
- **Experience Department**: Customer service & delivery focus  
- **User Experience Department**: Emotions & satisfaction focus
- **Business Department**: Market impact & business focus
- **Technical Department**: Features & specifications focus

### Layer 2: Master Sentiment Analyst
- Synthesizes all department inputs
- Makes expert final assessment
- Resolves conflicts between departments

### Layer 3: Business Advisor
- Provides actionable recommendations for sellers
- Business-focused improvement advice
- Ready for chatbot integration

## 🚀 Quick Start

### Basic Usage
```python
from workflow_manager import analyze_review

# Analyze a single review
result = analyze_review(
    review="Great product but terrible customer service",
    product_category="electronics"
)

# View results
print(f"Final sentiment: {result['master_analysis']['sentiment']}")
print(f"Department disagreement: {len(set([d['sentiment'] for d in result['department_analyses']]))}")
```

### Advanced Usage
```python
from workflow_manager import MultiAgentWorkflowManager

# Create workflow with custom settings
workflow = MultiAgentWorkflowManager(
    product_category="fashion",
    department_types=["quality", "experience", "user_experience"],
    max_tokens_per_department=200
)

# Run analysis
result = workflow.run_analysis("Review text here")
```

### Demo
```bash
python demo_enhanced_system.py
```

## 🔥 Key Features

### ✅ Real Agent Disagreement
- **Before**: All agents gave identical "mixed" results
- **After**: Departments disagree based on their specialization
  - Quality: "POSITIVE" (focuses on product)
  - Experience: "NEGATIVE" (focuses on service)
  - Master Analyst: Makes final expert decision

### ✅ Specialized Expertise
Each department agent is **extremely biased** toward their domain:
- Quality agent ignores service issues
- Experience agent ignores product quality  
- UX agent focuses only on emotions
- Business agent thinks only about ROI
- Technical agent cares only about specs

### ✅ Business-Ready Output
- Master analyst provides final sentiment
- Business advisor gives actionable recommendations
- Ready for chatbot integration
- Perfect for seller dashboards

### ✅ Simple Linear Workflow
- No complex LangGraph state management
- Clean Layer 1 → Layer 2 → Layer 3 pipeline
- Easy to understand and modify
- Fast processing (~15-17 seconds)

## 📊 Results Comparison

### Old System (Enhanced Coordinator)
```
Quality: mixed (0.85)
Experience: mixed (0.85) 
UX: mixed (0.85)
Business: mixed (0.85)
Technical: mixed (0.85)
→ All identical results!
```

### New System (3-Layer)
```
Quality: POSITIVE (0.85) ← Focuses on product
Experience: NEGATIVE (0.95) ← Focuses on service
UX: NEGATIVE (0.85) ← User frustration
Business: NEGATIVE (0.85) ← Business impact
Technical: POSITIVE (0.90) ← Technical specs
→ Master Analyst: NEGATIVE (0.87) ← Expert synthesis
→ Business Advisor: Specific recommendations
```

## 🛠️ File Structure

```
agents/
├── sentiment_agents.py          # All agent classes + factory
├── prompts/
│   ├── agent_prompts.py         # Department + Master + Advisor prompts
│   ├── base_prompts.py          # Common templates
│   └── product_prompts.py       # Product category customization
workflow_manager.py              # Main 3-layer workflow
demo_enhanced_system.py          # Complete demonstration
config.json                      # OpenAI API configuration
```

## 🎯 Use Cases

### E-commerce Platforms
- Product review analysis
- Seller improvement recommendations
- Customer sentiment monitoring

### Business Intelligence  
- Department-specific insights
- Prioritized improvement areas
- ROI-focused recommendations

### Chatbot Integration
- Business advisor output → Chatbot responses
- Seller support automation
- Customer service insights

## 🔧 Configuration

### Product Categories
- `electronics`: Smartphones, laptops, gadgets
- `fashion`: Clothing, accessories, shoes  
- `beauty`: Cosmetics, skincare, health products

### Department Selection
```python
# Use all 5 departments (default)
department_types=["quality", "experience", "user_experience", "business", "technical"]

# Or customize for specific needs
department_types=["quality", "experience"]  # Focus on product + service
```

### Token Limits
```python
max_tokens_per_department=150,  # Department agents
max_tokens_master=500,          # Master analyst
max_tokens_advisor=600          # Business advisor
```

## 📈 Performance

- **Processing Time**: ~15-17 seconds per review
- **Accuracy**: Real department disagreement achieved
- **Consistency**: Master analyst provides reliable synthesis
- **Scalability**: Linear workflow, easy to optimize

## 🎉 Success Metrics

1. **✅ Real Disagreement**: Departments now disagree based on specialization
2. **✅ Expert Synthesis**: Master analyst makes balanced decisions  
3. **✅ Business Value**: Actionable recommendations for sellers
4. **✅ Clean Architecture**: Simple linear workflow
5. **✅ Chatbot Ready**: Business advisor output perfect for conversations 