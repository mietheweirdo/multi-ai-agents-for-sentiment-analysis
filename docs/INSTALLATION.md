# 🚀 Installation & Setup Guide

## 📋 **Prerequisites**

### System Requirements
- **Python**: 3.9+ (Recommended: 3.11)
- **Operating System**: Windows 10/11, macOS, or Linux
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 2GB free space for dependencies

### Required API Keys
- **OpenAI API Key**: For GPT models (required)
- **Optional**: Other LLM provider keys for alternative models

## 🔧 **Installation Methods**

### Method 1: Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd multi-ai-agents-for-sentiment-analysis

# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Method 2: Pip + Virtual Environment

```bash
# Clone the repository
git clone <repository-url>
cd multi-ai-agents-for-sentiment-analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 3: Direct Installation

```bash
# Install directly (not recommended for development)
pip install -r requirements.txt
```

## ⚙️ **Configuration Setup**

### 1. Environment Configuration

Create a `config.json` file in the project root:

```json
{
  "openai": {
    "api_key": "your-openai-api-key-here",
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 500
  },
  "system": {
    "debug_mode": false,
    "enable_logging": true,
    "log_level": "INFO"
  },
  "agents": {
    "max_tokens_per_agent": 150,
    "max_tokens_consensus": 800,
    "enable_department_specialization": true
  },
  "data_pipeline": {
    "max_items_per_source": 50,
    "min_content_length": 20,
    "max_content_length": 2000,
    "enable_deduplication": true,
    "quality_threshold": 0.5
  }
}
```

### 2. Alternative: Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
DEBUG_MODE=false
LOG_LEVEL=INFO
```

## 🧪 **Verification & Testing**

### 1. Quick System Test

```bash
# Test basic functionality
python -c "from workflow_manager import analyze_review; print(analyze_review('This product is amazing!'))"
```

### 2. Run Full Test Suite

```bash
# 3-Layer system tests
python demo_enhanced_system.py

# LangGraph system tests  
python test_langgraph_system.py

# Evaluation suite
python evaluation/quick_test.py
```

### 3. Web Interface Test

```bash
# Start Streamlit app
streamlit run app.py
```

Expected output: Web interface accessible at `http://localhost:8501`

## 🔌 **A2A Protocol Setup (Optional)**

### 1. Install A2A Dependencies

```bash
pip install starlette uvicorn
```

### 2. Start A2A Servers

```bash
# Start all agent servers
python scripts/start_agents.py

# Or start individual agents
python -m rpc_servers.quality_agent_rpc
python -m rpc_servers.experience_agent_rpc
# ... other agents
```

### 3. Test A2A Communication

```bash
python scripts/test_a2a_workflow.py
```

## 📊 **Data Pipeline Setup**

### 1. Basic Data Directory Structure

```
multi-ai-agents-for-sentiment-analysis/
├── data/
│   ├── input/          # Input data files
│   ├── processed/      # Processed data
│   └── agent_ready/    # Agent-ready data
├── preprocessed_data/
└── charts/            # Generated visualizations
```

### 2. Sample Data Preparation

```python
# Create sample data for testing
from data_pipeline import create_sample_data

create_sample_data(
    output_dir="data/input",
    num_samples=100,
    categories=["electronics", "fashion", "books"]
)
```

## 🐳 **Docker Setup (Optional)**

### 1. Build Docker Image

```bash
# Build the image
docker build -t multi-agent-sentiment .

# Run container
docker run -p 8501:8501 -p 8000-8005:8000-8005 multi-agent-sentiment
```

### 2. Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8501:8501"
      - "8000-8005:8000-8005"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./config.json:/app/config.json
```

```bash
docker-compose up
```

## 🔍 **Troubleshooting**

### Common Issues

#### 1. Import Errors
```bash
# Solution: Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. API Key Errors
```bash
# Verify API key is set
python -c "import json; print(json.load(open('config.json'))['openai']['api_key'][:10] + '...')"
```

#### 3. Memory Issues
```bash
# Reduce token limits in config.json
{
  "agents": {
    "max_tokens_per_agent": 100,
    "max_tokens_consensus": 400
  }
}
```

#### 4. Port Conflicts (A2A Mode)
```bash
# Check if ports are in use
netstat -an | findstr :8000
netstat -an | findstr :8001

# Use different ports in scripts/start_agents.py
```

### Performance Optimization

#### 1. For Large Datasets
```json
{
  "data_pipeline": {
    "batch_size": 10,
    "parallel_processing": true,
    "max_workers": 4
  }
}
```

#### 2. For Cost Optimization
```json
{
  "openai": {
    "model": "gpt-3.5-turbo",
    "max_tokens": 300
  },
  "agents": {
    "max_tokens_per_agent": 100,
    "max_tokens_consensus": 300
  }
}
```

## 🎯 **Getting Started**

### Option 1: Web Interface (Easiest)
```bash
streamlit run app.py
```

### Option 2: Python API
```python
from workflow_manager import analyze_review

result = analyze_review(
    review="This smartphone has excellent camera quality!",
    product_category="electronics"
)
print(result)
```

### Option 3: A2A Protocol
```bash
# Start servers
python scripts/start_agents.py

# Use A2A client
python scripts/test_a2a_workflow.py
```

### Option 4: Command Line Demo
```bash
python demo_enhanced_system.py
```

## 📞 **Support**

### Self-Help Resources
1. Check `evaluation/` folder for example usage
2. Review `demo_enhanced_system.py` for comprehensive examples
3. Examine `test_langgraph_system.py` for advanced features

### System Health Check
```bash
python scripts/health_check.py
```

### Debug Mode
```json
{
  "system": {
    "debug_mode": true,
    "log_level": "DEBUG"
  }
}
```

