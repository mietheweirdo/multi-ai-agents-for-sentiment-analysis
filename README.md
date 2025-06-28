# Multi-AI Agents for Sentiment Analysis (A2A Compatible)

A sophisticated multi-agent sentiment analysis system using LangChain and LangGraph with OpenAI LLMs, fully integrated with the A2A (Agent-to-Agent) protocol. The system features specialized agents for different aspects of sentiment analysis with product-category-specific prompt customization, cost optimization, and A2A JSON-RPC endpoints following the Cross-Framework POC pattern.

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

## 🚀 Quick Start (A2A Mode)

### 1. Install Dependencies

```bash
# Install with Poetry (recommended)
pip install poetry
poetry install

# Or install with pip
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Start A2A Agent Servers

```bash
# Start all agents with monitoring
python scripts/start_agents.py

# Or start without monitoring
python scripts/start_agents.py --no-monitor

# Check agent health
python scripts/start_agents.py --health-check
```

### 4. Launch Streamlit Orchestrator

```bash
streamlit run app.py
```

### 5. Test A2A Workflow

```bash
# Test complete A2A workflow
python scripts/test_a2a_workflow.py

# Run test suite
pytest tests/ -v
```

## 🔧 A2A API Usage

### Direct RPC Calls

```bash
# Test quality agent
curl -X POST "http://localhost:8001/rpc" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": "test-123",
       "method": "tasks/send",
       "params": {
         "id": "test-123",
         "message": {
           "role": "user",
           "parts": [{"type": "text", "text": "This product has excellent build quality!"}]
         },
         "metadata": {
           "product_category": "electronics",
           "max_tokens": 150
         }
       }
     }'

# Test coordinator multi-agent analysis
curl -X POST "http://localhost:8000/rpc" \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": "coord-123",
       "method": "tasks/send",
       "params": {
         "id": "coord-123",
         "message": {
           "role": "user",
           "parts": [{"type": "text", "text": "Amazing smartphone with great camera but slow delivery."}]
         },
         "metadata": {
           "product_category": "electronics",
           "agent_types": ["quality", "experience", "user_experience", "business"],
           "max_tokens_per_agent": 150,
           "max_tokens_consensus": 800
         }
       }
     }'
```

### Python Integration

```python
import requests
import json
import uuid

def call_sentiment_agent(agent_port, review_text, metadata=None):
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tasks/send",
        "params": {
            "id": str(uuid.uuid4()),
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": review_text}]
            },
            "metadata": metadata or {}
        }
    }
    
    response = requests.post(f"http://localhost:{agent_port}/rpc", json=payload)
    result = response.json()
    
    # Extract analysis result
    analysis_json = result["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
    return json.loads(analysis_json)

# Analyze with quality agent
quality_result = call_sentiment_agent(
    8001, 
    "Excellent build quality and premium materials",
    {"product_category": "electronics", "max_tokens": 150}
)

print(f"Quality Sentiment: {quality_result['sentiment']}")
print(f"Confidence: {quality_result['confidence']:.2%}")
```

## 🚀 Legacy Quick Start

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

## 🧪 A2A Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Test RPC endpoints only
pytest tests/test_rpc_endpoints.py -v

# Test integration workflows
pytest tests/test_integration.py -v
```

### Integration Testing

```bash
# Test complete A2A workflow
python scripts/test_a2a_workflow.py

# Test individual components
python -m pytest tests/test_rpc_endpoints.py::TestQualityAgentRPC -v
```

### Load Testing

```bash
# Test concurrent requests (requires wrk or similar)
wrk -t4 -c10 -d30s --script=tests/load_test.lua http://localhost:8000/rpc
```

## � Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
COPY . .

RUN pip install poetry && poetry install --no-dev

EXPOSE 8000-8005

CMD ["python", "scripts/start_agents.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  sentiment-agents:
    build: .
    ports:
      - "8000-8005:8000-8005"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./.env:/app/.env
```

## �📊 A2A Output Format

### Individual Agent Response

```json
{
  "sentiment": "positive",
  "confidence": 0.85,
  "emotions": ["satisfied", "impressed"],
  "topics": ["build quality", "camera"],
  "reasoning": "Excellent product quality and premium features",
  "business_impact": "High customer satisfaction drives retention",
  "agent_type": "quality",
  "agent_name": "ProductQualityAgent"
}
```

### Coordinator Multi-Agent Response

```json
{
  "product_id": "sample_product",
  "product_category": "electronics",
  "review_text": "Amazing smartphone with great camera...",
  "agent_analyses": [
    {
      "agent_type": "quality",
      "sentiment": "positive",
      "confidence": 0.85,
      "emotions": ["satisfied", "impressed"],
      "topics": ["build quality", "camera"],
      "reasoning": "Excellent build quality and camera performance",
      "business_impact": "Strong product differentiation"
    },
    {
      "agent_type": "experience",
      "sentiment": "negative",
      "confidence": 0.75,
      "emotions": ["frustrated", "disappointed"],
      "topics": ["delivery", "customer service"],
      "reasoning": "Delivery delays and unresponsive service",
      "business_impact": "Customer retention risk"
    }
  ],
  "consensus": {
    "overall_sentiment": "mixed",
    "overall_confidence": 0.80,
    "agreement_level": "moderate",
    "key_insights": "Strong product quality offset by service issues",
    "business_recommendations": "Maintain product standards while improving delivery and service processes"
  },
  "analysis_metadata": {
    "total_agents": 4,
    "discussion_rounds": 2,
    "average_confidence": 0.80,
    "analysis_duration": 2.5,
    "agent_types_used": ["quality", "experience", "user_experience", "business"]
  }
}
```

## 📊 Legacy Output Format

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

## 🏗️ A2A Protocol Architecture

The system now follows the A2A (Agent-to-Agent) Cross-Framework POC pattern with JSON-RPC 2.0 endpoints:

```
📦 A2A Architecture
├── 🔗 JSON-RPC Endpoints (Port 8001-8005, 8000)
│   ├── quality_agent_rpc.py          # Product quality analysis
│   ├── experience_agent_rpc.py       # Customer service & delivery
│   ├── user_experience_agent_rpc.py  # Emotional responses & UX
│   ├── business_agent_rpc.py         # Market impact & business
│   ├── technical_agent_rpc.py        # Technical specifications
│   └── coordinator_agent_rpc.py      # Multi-agent orchestration
├── 🎯 Streamlit Orchestrator (app.py)
│   ├── Individual agent calls
│   ├── Sequential agent chains
│   └── Coordinated multi-agent analysis
├── 🛡️ Shared Infrastructure
│   ├── shared/json_rpc/base.py       # A2A utilities
│   └── shared/agent_cards/           # Agent capability descriptions
└── 🧪 A2A Testing Suite
    ├── tests/test_rpc_endpoints.py   # RPC endpoint tests
    └── tests/test_integration.py     # End-to-end workflow tests
```

### 🔌 A2A JSON-RPC Endpoints

Each specialized agent exposes a JSON-RPC 2.0 endpoint following A2A protocol:

**Request Format:**
```json
{
  "jsonrpc": "2.0",
  "id": "<uuid>",
  "method": "tasks/send",
  "params": {
    "id": "<uuid>",
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "<review_text>"}]
    },
    "metadata": {
      "product_category": "electronics",
      "max_tokens": 150
    }
  }
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": "<same_uuid>",
  "result": {
    "artifacts": [
      {
        "parts": [{
          "text": {"raw": "<analysis_json>"}
        }]
      }
    ]
  }
}
```

### 🚀 A2A Agent Endpoints

| Agent | Port | Endpoint | Specialization |
|-------|------|----------|----------------|
| **Quality Agent** | 8001 | `/rpc` | Product quality, durability, manufacturing |
| **Experience Agent** | 8002 | `/rpc` | Customer service, delivery, support |
| **User Experience Agent** | 8003 | `/rpc` | Emotional responses, satisfaction |
| **Business Agent** | 8004 | `/rpc` | Market impact, business implications |
| **Technical Agent** | 8005 | `/rpc` | Technical specs, features, performance |
| **Coordinator Agent** | 8000 | `/rpc` | Multi-agent orchestration |

Each agent also provides:
- `/.well-known/agent.json` - A2A agent capability card
- `/health` - Health check endpoint
- `/config` - Configuration information (coordinator only)

## ✅ Deployment Status

**🎉 FULLY OPERATIONAL**: The multi-agent sentiment analysis system has been successfully refactored to follow the A2A Cross-Framework POC pattern and is now fully operational!

### Current Status
- ✅ **All 6 Agents Running**: Quality, Experience, User Experience, Business, Technical, and Coordinator agents
- ✅ **A2A Protocol Compliant**: All agents expose JSON-RPC 2.0 endpoints with proper error handling
- ✅ **Health Checks Passing**: All agents respond to health endpoints 
- ✅ **Agent Cards Available**: A2A-compliant agent discovery at `/.well-known/agent.json`
- ✅ **Streamlit UI Active**: Interactive orchestrator running on http://localhost:8501
- ✅ **Integration Tests Passing**: All workflow tests completed successfully

### Live Endpoints
```
Quality Agent:       http://localhost:8001 (RPC: /rpc, Health: /health)
Experience Agent:    http://localhost:8002 (RPC: /rpc, Health: /health)  
User Experience:     http://localhost:8003 (RPC: /rpc, Health: /health)
Business Agent:      http://localhost:8004 (RPC: /rpc, Health: /health)
Technical Agent:     http://localhost:8005 (RPC: /rpc, Health: /health)
Coordinator:         http://localhost:8000 (RPC: /rpc, Health: /health)
Streamlit UI:        http://localhost:8501
```

### Test Results
- **Individual Agents**: All 5 specialized agents correctly analyzed test reviews with 75-90% confidence
- **Coordinator Workflow**: Successfully orchestrated multi-agent analysis achieving 83% consensus confidence
- **Response Time**: ~24 seconds for full multi-agent consensus analysis
- **Agreement Level**: Medium agreement across agents for complex sentiment scenarios
