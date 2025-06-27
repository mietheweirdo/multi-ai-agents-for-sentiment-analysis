# Multi-AI Agents for Sentiment Analysis

A sophisticated multi-agent sentiment analysis system using LangChain and LangGraph with OpenAI LLMs and the A2A protocol. The system features specialized agents for different aspects of sentiment analysis with product-category-specific prompt customization and cost optimization.

## 🏗️ Architecture Overview

The system uses an organized, maintainable architecture with structured prompt management:

```
agents/
├── prompts/                    # 🆕 Organized prompt structure
│   ├── __init__.py            # Module initialization
│   ├── base_prompts.py        # Common templates and utilities
│   ├── agent_prompts.py       # Agent-specific prompts
│   ├── product_prompts.py     # Product-category customizations
│   └── coordinator_prompts.py # Consensus and discussion prompts
├── sentiment_agents.py        # Specialized sentiment analysis agents
├── enhanced_coordinator.py    # Multi-agent coordination with LangGraph
├── product_prompts.py         # Legacy product prompt manager
├── scraper.py                 # Review scraping functionality
├── preprocessor.py            # Text preprocessing
├── memory_manager.py          # Memory management
└── reporter.py                # Report generation
```

## 🎯 Key Features

### **Organized Prompt Structure** 🆕
- **Dedicated prompt files** for better maintainability
- **Separation of concerns** with base, agent, product, and coordinator prompts
- **Easy to read, understand, and maintain** prompt structure
- **Product-category-specific customization** for specialized analysis

### **Specialized Agents**
- **Product Quality Agent**: Analyzes quality, durability, and manufacturing aspects
- **Customer Experience Agent**: Focuses on service, delivery, and support experiences
- **User Experience Agent**: Evaluates emotional responses and user satisfaction
- **Business Impact Agent**: Assesses market implications and business metrics
- **Technical Specification Agent**: Analyzes technical features and performance

### **Cost Optimization**
- **Configurable token limits** per agent (default: 150 tokens)
- **Efficient prompt design** to minimize API costs
- **Token usage tracking** and optimization

### **Product-Category Customization**
- **Electronics**: Technical performance, battery life, build quality
- **Fashion**: Fabric quality, fit, style, comfort
- **Home & Garden**: Durability, functionality, safety
- **Beauty & Health**: Effectiveness, ingredients, results
- **Sports & Outdoors**: Performance, durability, safety
- **Books & Media**: Content quality, educational value

### **Multi-Agent Consensus**
- **LangGraph workflow** for agent coordination
- **Discussion rounds** for consensus building
- **Weighted confidence scoring**
- **Business impact assessment**

## 🎯 Business Recommendations Configuration

The system now supports configurable business recommendations length to meet different needs:

### Configuration Parameters

- **`max_tokens_consensus`**: Controls the token limit for consensus analysis (default: 800)
- **`max_tokens_per_agent`**: Controls individual agent token limits (default: 150)
- **Word limits in prompts**: Business recommendations can be up to 300 words

### Usage Examples

#### 1. Standard Configuration (Cost-Optimized)
```python
coordinator = EnhancedCoordinatorAgent(
    config=config,
    product_category="electronics",
    max_tokens_per_agent=150,
    max_tokens_consensus=300  # Shorter recommendations
)
```

#### 2. Enhanced Configuration (Balanced)
```python
coordinator = EnhancedCoordinatorAgent(
    config=config,
    product_category="electronics", 
    max_tokens_per_agent=400,
    max_tokens_consensus=800  # Detailed recommendations
)
```

#### 3. Premium Configuration (Maximum Detail)
```python
coordinator = EnhancedCoordinatorAgent(
    config=config,
    product_category="electronics",
    max_tokens_per_agent=600,
    max_tokens_consensus=1200  # Comprehensive business insights
)
```

#### 4. API Usage
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": ["Your review text here"],
    "product_category": "electronics",
    "max_tokens_per_agent": 400,
    "max_tokens_consensus": 800
  }'
```

### Cost Considerations

- **Standard (300 tokens)**: ~$0.000045 per analysis
- **Enhanced (800 tokens)**: ~$0.00012 per analysis  
- **Premium (1200 tokens)**: ~$0.00018 per analysis

*Costs are approximate for GPT-4o-mini model*

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Create a `config.json` file:

```json
{
    "api_key": "your-openai-api-key",
    "model_name": "gpt-4o-mini"
}
```

### 3. Basic Usage

```python
from agents.enhanced_coordinator import EnhancedCoordinatorAgent
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize coordinator
coordinator = EnhancedCoordinatorAgent(
    config=config,
    product_category="electronics",
    agent_types=["quality", "experience", "user_experience", "business"],
    max_tokens_per_agent=150
)

# Analyze reviews
result = coordinator.run_workflow(
    reviews=["This smartphone is amazing! Great camera and battery life."]
)

print(f"Sentiment: {result['consensus']['overall_sentiment']}")
print(f"Confidence: {result['consensus']['overall_confidence']:.2f}")
```

### 4. Run Demo

```bash
python demo_enhanced_system.py
```

## 📁 Prompt Organization

### **Base Prompts** (`agents/prompts/base_prompts.py`)
- Common system message templates
- Human message templates
- Error handling templates
- Utility functions for formatting and validation

### **Agent Prompts** (`agents/prompts/agent_prompts.py`)
- Specialized prompts for each agent type
- Role-specific instructions and focus areas
- Token limit warnings and constraints

### **Product Prompts** (`agents/prompts/product_prompts.py`)
- Product-category-specific focus areas
- Customization logic for different product types
- Category descriptions and metadata

### **Coordinator Prompts** (`agents/prompts/coordinator_prompts.py`)
- Consensus building prompts
- Discussion phase prompts
- Summary and reporting templates

## 🔧 API Usage

### FastAPI Server

```bash
python enhanced_a2a_server.py
```

**Endpoints:**
- `POST /analyze`: Analyze reviews with multi-agent system
- `GET /categories`: Get available product categories
- `GET /agents`: Get available agent types

### Example API Call

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "reviews": ["This product is excellent!"],
       "product_category": "electronics",
       "agent_types": ["quality", "experience", "user_experience"],
       "max_tokens_per_agent": 150
     }'
```

## 🎛️ Configuration Options

### Agent Types
- `quality`: Product quality and durability analysis
- `experience`: Customer service and delivery experience
- `user_experience`: Emotional response and satisfaction
- `business`: Market impact and business implications
- `technical`: Technical specifications and features

### Product Categories
- `electronics`: Electronic devices and technology
- `fashion`: Clothing and accessories
- `home_garden`: Home improvement and garden products
- `beauty_health`: Beauty and health products
- `sports_outdoors`: Sports equipment and outdoor gear
- `books_media`: Books and digital media

### Token Limits
- **Conservative**: 100 tokens per agent
- **Balanced**: 150 tokens per agent (default)
- **Detailed**: 200+ tokens per agent

## 📊 Output Format

```json
{
  "product_id": "sample_product",
  "product_category": "electronics",
  "review_text": "This smartphone is amazing!",
  "agent_analyses": [
    {
      "agent_type": "quality",
      "sentiment": "positive",
      "confidence": 0.85,
      "emotions": ["satisfied", "impressed"],
      "topics": ["build quality", "performance"],
      "reasoning": "Excellent build quality and performance",
      "business_impact": "High customer satisfaction"
    }
  ],
  "consensus": {
    "overall_sentiment": "positive",
    "overall_confidence": 0.82,
    "agreement_level": "high",
    "key_insights": "Strong positive sentiment across all aspects",
    "business_recommendations": "Continue current quality standards"
  },
  "analysis_metadata": {
    "total_agents": 4,
    "discussion_rounds": 1,
    "average_confidence": 0.82,
    "analysis_timestamp": "2024-01-15T10:30:00"
  }
}
```

## 🤝 Contributing

1. Follow the organized prompt structure
2. Maintain separation of concerns
3. Add comprehensive tests
4. Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with LangChain and LangGraph
- Uses OpenAI's GPT models for analysis
