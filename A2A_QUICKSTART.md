# 🚀 A2A LangGraph Multi-Agent System - Quick Start Guide

## 🎯 Overview

Your chatbot now uses the **Google Agent-to-Agent (A2A) protocol** with **LangGraph consensus and debate workflow**. This enables:

- ✅ **Agent-to-Agent Communication**: Structured JSON-RPC 2.0 protocol
- ✅ **Multi-Agent Consensus**: Agents discuss and reach agreements
- ✅ **Debate & Discussion**: Agents can disagree and refine their analyses
- ✅ **Disagreement Detection**: Automatic detection of conflicting opinions
- ✅ **Consensus Building**: Iterative refinement until agreement

## 🏗️ Streamlit Chatbot Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           🌐 STREAMLIT WEB INTERFACE                                │
│                               (app_a2a.py)                                          │
│                                                                                     │
│  ┌─────────────────┐    ┌──────────────────┐    ┌────────────────────────────────┐ │
│  │  💬 Chat Input  │ -> │  🔍 Product      │ -> │  📊 Response Display           │ │
│  │  (user query)   │    │    Detection     │    │  (formatted result)           │ │
│  │                 │    │  (LLM-powered)   │    │                                │ │
│  └─────────────────┘    └──────────────────┘    └────────────────────────────────┘ │
│                                 │                              ↑                  │
└─────────────────────────────────┼──────────────────────────────┼──────────────────┘
                                  │                              │
                                  ▼                              │
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        📡 DATA SCRAPING PIPELINE                                    │
│                           (data_pipeline/)                                          │
│                                                                                     │
│  ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ 🔍 Keyword       │ -> │ 🌐 Multi-Source │ -> │ 🧹 Advanced Preprocessing      │ │
│  │   Extraction     │    │   Scraping      │    │   & Quality Filtering          │ │
│  │                  │    │ • YouTube API   │    │ • Text normalization           │ │
│  │                  │    │ • Tiki Scraper  │    │ • Sentiment preprocessing      │ │
│  └──────────────────┘    └─────────────────┘    └─────────────────────────────────┘ │
│                                                              │                     │
└──────────────────────────────────────────────────────────────┼─────────────────────┘
                                                               │
                                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    🤖 A2A LANGGRAPH COORDINATOR                                     │
│                   (rpc_servers/langgraph_coordinator_rpc.py)                       │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        📨 JSON-RPC 2.0 A2A PROTOCOL                            │ │
│  │                           (Port 8010/8011)                                     │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                             │
│                                      ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                       🏭 LANGGRAPH WORKFLOW ENGINE                              │ │
│  │                                                                                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │ │
│  │  │ 🔬 Quality  │  │ 👥 Customer │  │ 🎯 User     │  │ 💼 Business │  │ ⚙️ Tech │ │ │
│  │  │   Agent     │  │ Experience  │  │ Experience  │  │   Impact    │  │ Specs  │ │ │
│  │  │             │  │   Agent     │  │   Agent     │  │   Agent     │  │ Agent  │ │ │
│  │  │ GPT-4o-mini │  │ GPT-4o-mini │  │ GPT-4o-mini │  │ GPT-4o-mini │  │GPT-4o..│ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘ │ │
│  │           ↕               ↕               ↕               ↕               ↕      │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │              🧠 DISAGREEMENT DETECTION & CONSENSUS ENGINE                   │ │ │
│  │  │                      (threshold: 0.6, max rounds: 2)                      │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                      │                                         │ │
│  │                ┌─────────────────────┼─────────────────────┐                   │ │
│  │                ▼                     ▼                     ▼                   │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────────┐ │ │
│  │  │  🔄 Discussion      │  │  ✅ Direct to       │  │  👑 Master Analyst       │ │ │
│  │  │     Rounds          │  │     Synthesis       │  │     Synthesis            │ │ │
│  │  │  (If disagreement)  │  │  (If consensus)     │  │  (Final reasoning)       │ │ │
│  │  └─────────────────────┘  └─────────────────────┘  └──────────────────────────┘ │ │
│  │                │                                                ↓              │ │
│  │                └─────────────────┐                              ▼              │ │
│  │                                  ▼                  ┌──────────────────────────┐ │ │
│  │                      ┌─────────────────────────────────────────────────────────┐ │ │
│  │                      │         💡 Business Advisor Agent                       │ │ │
│  │                      │       (Strategic recommendations)                      │ │ │
│  │                      └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                             │
│                                      ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                    📋 A2A COMPLIANT RESPONSE FORMATTING                        │ │
│  │                                                                                 │ │
│  │  {                                                                              │ │
│  │    "jsonrpc": "2.0",                                                            │ │
│  │    "result": {                                                                  │ │
│  │      "artifacts": [{                                                            │ │
│  │        "parts": [{"type": "text", "text": {"raw": "JSON_ANALYSIS_RESULT"}}]    │ │
│  │      }]                                                                         │ │
│  │    }                                                                            │ │
│  │  }                                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      🎨 RESPONSE FORMATTING & DISPLAY                               │
│                      (agents/response_agent.py)                                    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                    📝 HUMAN-READABLE RESPONSE GENERATION                        │ │
│  │                                                                                 │ │
│  │  • Parse A2A JSON result                                                       │ │
│  │  • Extract consensus & agent analyses                                          │ │
│  │  • Format discussion transcripts                                               │ │
│  │  • Generate personalized recommendations                                       │ │
│  │  • Add metadata (processing time, review count, etc.)                         │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘

📊 TECHNOLOGY STACK:
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ • Frontend: Streamlit (Python web framework)                                       │
│ • Backend: FastAPI (A2A RPC server)                                                │
│ • Protocol: JSON-RPC 2.0 (Google A2A standard)                                    │
│ • AI Engine: OpenAI GPT-4o-mini                                                    │
│ • Orchestration: LangGraph (agent workflow management)                             │
│ • Data Sources: YouTube API, Tiki web scraping                                     │
│ • Processing: Advanced text preprocessing pipeline                                 │
│ • Communication: HTTP requests with JSON payloads                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

## 🔄 Key Technical Improvements vs Original app.py

### 📈 **Enhanced Backend Architecture**
| Feature | Original app.py | New app_a2a.py |
|---------|----------------|-----------------|
| **Agent Communication** | Direct function calls | A2A JSON-RPC protocol |
| **Workflow Management** | Linear 3-layer process | LangGraph state machine |
| **Consensus Building** | Fixed agent hierarchy | Dynamic discussion rounds |
| **Error Handling** | Basic try/catch | A2A-compliant error responses |
| **Scalability** | Monolithic | Microservice-ready |
| **Monitoring** | Limited logs | Full A2A audit trail |

### 🤖 **Advanced Agent Capabilities**
- **Disagreement Detection**: Automatically triggers discussion when agents disagree (threshold: 0.6)
- **Iterative Refinement**: Agents can refine their analyses through discussion rounds
- **Consensus Tracking**: Real-time monitoring of agreement levels between agents
- **Discussion Transcripts**: Full conversation logs preserved in A2A response
- **Dynamic Agent Selection**: Choose which agents participate in analysis

### 🔧 **Protocol Benefits**
- **Interoperability**: Standard JSON-RPC 2.0 format for easy integration
- **Enterprise Ready**: A2A protocol compliance for business environments
- **Async Support**: Non-blocking agent communication
- **Version Control**: Protocol versioning for backward compatibility
- **Audit Trail**: Complete request/response logging for compliance
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.a2a_example .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 2. Install Dependencies

```bash
# Make sure you have LangGraph
pip install langgraph

# Install other requirements
pip install -r requirements.txt
```

### 3. Start A2A LangGraph Coordinator

```bash
# Start the A2A coordinator server (required for backend)
python rpc_servers/langgraph_coordinator_rpc.py

# The coordinator will start on port 8010
# You should see: "🚀 Starting LangGraph Multi-Agent Coordinator RPC Server on port 8010"
python rpc_servers/langgraph_coordinator_rpc.py
```

You should see:
```
🚀 Starting LangGraph Multi-Agent Coordinator RPC Server on port 8010
🔗 Agent Card: http://localhost:8010/.well-known/agent.json
❤️ Health Check: http://localhost:8010/health
🤖 RPC Endpoint: http://localhost:8010/rpc
```

### 4. Run A2A Streamlit App

```bash
# Start the A2A-compliant chatbot (port 8512 to avoid conflicts)
streamlit run app_a2a.py --server.port 8512
```

The app will be available at: `http://localhost:8512`

## 🎮 Usage Examples

### Basic A2A Request

```python
import requests
import uuid

# Create A2A payload
payload = {
    "jsonrpc": "2.0",
    "id": str(uuid.uuid4()),
    "method": "tasks/send",
    "params": {
        "id": str(uuid.uuid4()),
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": "Should I buy iPhone 15?"}]
        },
        "metadata": {
            "product_category": "electronics",
            "max_discussion_rounds": 2,
            "disagreement_threshold": 0.6,
            "enable_consensus_debate": True
        }
    }
}

# Call A2A coordinator
response = requests.post("http://localhost:8010/rpc", json=payload)
result = response.json()
```

### A2A Response Format

```json
{
    "jsonrpc": "2.0",
    "id": "task-123",
    "result": {
        "artifacts": [{
            "parts": [{
                "type": "text",
                "text": {
                    "raw": "{
                        \"consensus\": {
                            \"overall_sentiment\": \"positive\",
                            \"overall_confidence\": 0.85,
                            \"agreement_level\": \"high\"
                        },
                        \"agent_analyses\": [...],
                        \"discussion_info\": {
                            \"discussion_rounds\": 0,
                            \"consensus_reached\": true,
                            \"disagreement_level\": 0.2
                        }
                    }"
                }
            }]
        }]
    }
}
```

## 📊 Real-Time Data Flow Example

### Streamlit Chat Processing Steps

```
1. 💬 User Input: "Should I buy Samsung Z-Fold?"
   └─ Streamlit captures user message
   
2. 🔍 Product Detection (LLM-powered):
   ├─ Input: "Should I buy Samsung Z-Fold?"
   ├─ LLM Analysis: Extract product info using GPT-4o-mini
   └─ Output: {
        "product_name": "Samsung Galaxy Z-Fold",
        "category": "electronics", 
        "question_type": "purchase_advice",
        "search_keywords": "samsung galaxy fold"
      }

3. 🌐 Data Scraping Pipeline:
   ├─ Keywords: "samsung galaxy fold"
   ├─ YouTube API: Fetch video reviews & comments (max 3 per source)
   ├─ Tiki Scraper: Extract product reviews & ratings  
   ├─ Preprocessing: Clean text, normalize ratings
   └─ Output: [9 processed reviews ready for analysis]

4. 🤖 A2A LangGraph Coordinator Call:
   ├─ Create JSON-RPC payload with scraped reviews
   ├─ HTTP POST to localhost:8010/rpc
   ├─ Timeout: 60 seconds
   └─ Metadata: {
        "agent_types": ["quality", "experience", "user_experience", "business", "technical"],
        "max_discussion_rounds": 2,
        "disagreement_threshold": 0.6
      }

5. 🏭 LangGraph Multi-Agent Processing:
   ├─ Initialize 5 specialized agents (Quality, Experience, UX, Business, Technical)
   ├─ Each agent analyzes reviews independently
   ├─ Results: quality=positive(0.85), experience=neutral(0.70), ux=positive(0.80), 
   │          business=positive(0.75), technical=positive(0.85)
   ├─ Disagreement Level: 0.25 (< 0.6 threshold)
   ├─ Consensus: ✅ REACHED (no discussion needed)
   ├─ Master Analyst: Synthesize all analyses → positive(0.81)
   └─ Business Advisor: Generate strategic recommendations

6. 📨 A2A Response Generation:
   ├─ Format as JSON-RPC 2.0 compliant response
   ├─ Embed analysis result in A2A artifacts structure
   └─ Include metadata: processing_time=15.2s, consensus=true

7. 🎨 Response Formatting (ProductResponseAgent):
   ├─ Parse A2A JSON result
   ├─ Extract consensus & individual agent analyses  
   ├─ Generate human-readable response with recommendations
   └─ Add chat metadata (product, review count, time)

8. 💬 Streamlit Display:
   ├─ Show assistant response in chat bubble
   ├─ Display metadata: "Product: Samsung Galaxy Z-Fold • Reviews analyzed: 9 • Time: 15.2s"
   └─ Update chat history for conversation context
```

### Performance Metrics
- **Average Response Time**: 10-25 seconds (depending on discussion rounds)
- **API Calls**: 7-15 OpenAI requests (5 agents + 1 master + 1 advisor + potential discussion)
- **Data Sources**: YouTube API + Tiki web scraping
- **Concurrent Processing**: Agents run sequentially but with async potential
- **Memory Usage**: ~50MB for full pipeline execution

## ⚙️ Configuration Options

### LangGraph Settings

- **max_discussion_rounds**: 0-5 (default: 2)
  - 0 = No discussion (fast)
  - 2-3 = Balanced (recommended) 
  - 5 = Thorough discussion (slow)

- **disagreement_threshold**: 0.0-1.0 (default: 0.6)
  - 0.0 = Always discuss (thorough)
  - 0.6 = Balanced sensitivity
  - 1.0 = Never discuss (fast)

- **agent_types**: Array of agents to use
  - Available: quality, experience, user_experience, business, technical
  - Default: All 5 agents

### Product Categories

- electronics
- fashion  
- home_garden
- books
- sports
- automotive

## 🔍 Monitoring & Debugging

### Health Check

```bash
curl http://localhost:8010/health
```

### Agent Card

```bash
curl http://localhost:8010/.well-known/agent.json
```

### View Discussion Logs

The A2A response includes full discussion transcripts:

```json
{
    "discussion_info": {
        "discussion_messages": [
            "QUALITY: positive - Great build quality and materials",
            "BUSINESS: negative - Overpriced for current market conditions",
            "QUALITY: positive - Reconsidering, premium pricing justified by quality"
        ],
        "discussion_rounds": 2,
        "consensus_reached": true
    }
}
```

## 🎯 Key Features

### 1. Automatic Consensus Detection
- Agents automatically detect when they disagree
- Triggers discussion rounds only when needed
- Saves cost and time for clear-cut cases

### 2. Structured Agent Debate
- Each agent maintains their specialized perspective
- Agents can refine their analyses based on discussion
- Full transcript preserved for transparency

### 3. A2A Protocol Compliance
- Standard JSON-RPC 2.0 format
- Google A2A artifact structure
- Compatible with A2A ecosystem

### 4. Flexible Agent Selection
- Choose which agents to include
- Customize discussion parameters
- Enable/disable debate features

## 🚨 Troubleshooting

### ❌ "Connection refused" Error
```bash
# Check if coordinator is running
netstat -ano | findstr :8010

# If not running, start it:
python rpc_servers/langgraph_coordinator_rpc.py

# If port is in use, kill the process and restart:
# On Windows: taskkill /PID <PID> /F
# Then restart the coordinator
```

### ❌ "A2A coordinator error: None" 
This was a common issue - the error checking logic was treating `"error": None` as an error.

**✅ Fixed in current version**: The system now properly checks `if "error" in result and result.get("error") is not None`

### ❌ API Key Issues
```bash
# Verify API key is loaded correctly
echo $OPENAI_API_KEY

# Check .env file exists
cat .env

# Restart coordinator after fixing API key
python rpc_servers/langgraph_coordinator_rpc.py
```

### ❌ "Timeout not available" Message
This message appears on Windows systems due to signal limitations, but doesn't affect functionality.

**Expected behavior**: System falls back to Windows-compatible scraping automatically.

### 🔧 Verification Commands
```bash
# Test coordinator health
curl http://localhost:8010/health

# Test simple A2A call
python test_a2a_quick_fix.py

# Check coordinator logs for API calls
# Should see: "HTTP/1.1 200 OK" for successful OpenAI API calls
```

### 📊 Performance Tuning
```bash
# For faster responses (fewer agents):
metadata = {
    "agent_types": ["quality", "experience"],  # Just 2 agents
    "max_discussion_rounds": 1,
    "disagreement_threshold": 0.8  # Less likely to trigger discussion
}

# For more thorough analysis:
metadata = {
    "agent_types": ["quality", "experience", "user_experience", "business", "technical"],
    "max_discussion_rounds": 3,
    "disagreement_threshold": 0.4  # More likely to trigger discussion
}
```

## 🎉 Success!

Your chatbot now has:
- ✅ Full A2A protocol compliance
- ✅ LangGraph consensus workflow  
- ✅ Agent debate capabilities
- ✅ Disagreement detection
- ✅ Transparent discussion logs

Enjoy your advanced multi-agent system! 🤖✨
