# 🔄 LangGraph Multi-Agent Sentiment Analysis

## 🎯 **Files Created:**

```
📁 Project Structure
├── agents/
│   └── langgraph_coordinator.py     # ⭐ Main LangGraph coordinator
├── test_langgraph_system.py         # 🧪 Comprehensive test suite
├── visualize_langgraph.py           # 📊 Workflow visualization
└── LANGGRAPH_SETUP.md              # 📖 This file
```

## 🚀 **Quick Start:**

### 1. Install Dependencies
```bash
pip install langgraph matplotlib
```

### 2. Run Tests
```bash
# Full test suite with different scenarios
python test_langgraph_system.py

# Or quick single test
python -c "from agents.langgraph_coordinator import analyze_with_langgraph; print(analyze_with_langgraph('Great product!'))"
```

### 3. Visualize Workflows
```bash
python visualize_langgraph.py
```

## 🔄 **LangGraph vs Manual Comparison:**

| Feature | Manual | LangGraph |
|---------|--------|-----------|
| **Agent Communication** | ❌ None | ✅ Discussion rounds |
| **Consensus Detection** | ❌ None | ✅ Automatic |
| **API Calls** | 7 fixed | 7-22 dynamic |
| **Cost** | Low | Variable |
| **Complexity** | Simple | Advanced |
| **Explainability** | Basic | Detailed |

## 📊 **Key Features:**

### 🗣️ **Agent Discussion:**
```python
# Agents can "argue" and refine their analyses
Quality Agent: "positive - great build quality"
Business Agent: "negative - overpriced"
→ Discussion round → Both refine opinions
```

### 🎯 **Consensus Detection:**
```python
disagreement_level = 0.8  # 80% disagreement
if disagreement_level > threshold:
    → Trigger discussion
else:
    → Proceed to synthesis
```

### 📈 **Dynamic Workflow:**
```python
# Path 1: Consensus (fast)
5 Agents → Check → ✅ Agree → Master → End

# Path 2: Discussion (thorough)
5 Agents → Check → ❌ Disagree → Discussion → Refine → Check → Master → End
```

## 🎮 **Usage Examples:**

### Basic Usage:
```python
from agents.langgraph_coordinator import analyze_with_langgraph

result = analyze_with_langgraph(
    review="Great phone but expensive",
    product_category="electronics",
    max_discussion_rounds=2,
    disagreement_threshold=0.6
)

print(f"Final sentiment: {result['master_analysis']['sentiment']}")
print(f"Discussion rounds: {result['workflow_metadata']['discussion_rounds']}")
```

### Advanced Usage:
```python
from agents.langgraph_coordinator import LangGraphCoordinator

coordinator = LangGraphCoordinator(
    product_category="fashion",
    department_types=["quality", "user_experience", "business"],
    max_discussion_rounds=3,
    disagreement_threshold=0.5
)

result = coordinator.run_analysis("Love the style but quality issues")
```

## 🎯 **When to Use:**

### ✅ **Use LangGraph When:**
- Need explainable AI with agent reasoning
- Handling complex/contradictory reviews  
- Research/experimentation priority
- Want advanced AI capabilities showcase
- Need workflow transparency

### ❌ **Use Manual When:**
- Need fast, cost-efficient analysis
- Reviews are straightforward
- Production stability priority
- Simple maintenance preferred
- Budget constraints

## 🔧 **Configuration:**

### Disagreement Threshold:
```python
# Lower = Less discussion (faster, cheaper)
disagreement_threshold=0.4  # Discuss only if >40% disagree

# Higher = More discussion (thorough, expensive)  
disagreement_threshold=0.8  # Discuss if >80% disagree
```

### Discussion Rounds:
```python
max_discussion_rounds=1  # Quick refinement
max_discussion_rounds=3  # Thorough discussion
```

## 📊 **Cost Analysis:**

```
Manual Workflow:     $0.00084 per analysis
LangGraph (no disc): $0.00084 per analysis  (same)
LangGraph (1 round): $0.00144 per analysis  (1.7x)
LangGraph (2 rounds): $0.00204 per analysis  (2.4x)
```

## 🎉 **Demo Output:**
```
🟢 TEST CASE 1: CONSENSUS EXPECTED
📊 Analysis Results
Review: This phone is absolutely fantastic! The camera quality is stunning...
💬 AGENT DISCUSSION: No discussion needed (consensus reached)
⚙️ WORKFLOW METADATA:
  Discussion Rounds: 0
  Disagreement Level: 0.20
  Consensus Reached: True

🔴 TEST CASE 2: DISAGREEMENT EXPECTED  
📊 Analysis Results
💬 AGENT DISCUSSION (5 messages):
  1. QUALITY: positive - Amazing build quality and premium materials but pricing concerns...
  2. BUSINESS: negative - Overpriced for market positioning and competitive landscape...
⚙️ WORKFLOW METADATA:
  Discussion Rounds: 2
  Disagreement Level: 0.80
  Consensus Reached: True (after discussion)
```

**🎊 Enjoy your new LangGraph Multi-Agent System!** 