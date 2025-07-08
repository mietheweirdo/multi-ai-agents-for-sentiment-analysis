# Evaluation System

Clean, organized evaluation system for comparing different sentiment analysis approaches.

## 🏗️ Structure

```
evaluation/
├── compare_single_vs_langchain.py     # Single Agent vs LangChain comparison
├── compare_manual_vs_langchain.py     # Manual Workflow vs LangChain comparison
├── print_summary.py                   # Summary of all evaluation results
├── datasets/
│   ├── langchain_vs_single_dataset.json    # Complex cases favoring LangChain discussion
│   ├── langchain_vs_manual_dataset.json    # Conflict resolution cases
│   ├── simple_cases_dataset.json           # Clear-cut cases favoring single agent
│   └── labeled_dataset.json                # Original complex cases (archived)
├── results/
│   ├── single_vs_langchain_YYYYMMDD_HHMMSS.json
│   ├── manual_vs_langchain_YYYYMMDD_HHMMSS.json
│   └── ...
└── archive/                           # Old evaluation files
```

## 🚀 Usage

### Run Individual Comparisons

```bash
# Compare Single Agent vs LangChain
python evaluation/compare_single_vs_langchain.py

# Compare Manual Workflow vs LangChain  
python evaluation/compare_manual_vs_langchain.py
```

### View Results Summary

```bash
# View summary of all evaluations
python evaluation/print_summary.py
```

## 📊 What Each Comparison Tests

### Single Agent vs LangChain
- **Single Agent**: Direct sentiment analysis with single specialized agent
- **LangChain**: Multi-agent discussion system with consensus building
- **Key Metrics**: Accuracy, confidence, processing time, discussion rounds

### Manual Workflow vs LangChain  
- **Manual Workflow**: Linear 3-layer pipeline (Departments → Master → Business)
- **LangChain**: Discussion-based consensus with conflict resolution
- **Key Metrics**: Accuracy, confidence, processing time, discussion capability

## 📈 Result Files

Each result file contains:
- **test_metadata**: What workflows were compared, when, dataset used
- **results**: Category-by-category performance data
- **workflow_metadata**: Discussion rounds, consensus info, processing time

## 🎯 Expected Performance

Based on dataset design:
- **LangChain should excel**: Complex trade-offs requiring multi-perspective analysis
- **Single Agent should excel**: Simple, clear-cut sentiment cases
- **Manual Workflow**: Linear analysis without conflict resolution
- **Discussion advantage**: LangChain's consensus building for complex cases

## 🔍 Understanding Results

The `print_summary.py` script provides:
1. **Available Results**: List of all evaluation files
2. **Latest Performance**: Comparison table with winners
3. **Key Findings**: Overall trends and recommendations  
4. **Detailed Breakdown**: Category-by-category analysis

## 📝 Datasets Strategy

### **LangChain vs Single Dataset** (`langchain_vs_single_dataset.json`)
Designed to showcase LangChain's discussion advantages:
- **Complex trade-offs**: Performance vs portability, quality vs price
- **Multi-perspective analysis**: Cases requiring different viewpoints
- **Nuanced reasoning**: Where single agents might oversimplify
- **Ground truth**: Only positive, negative, neutral (no "mixed")

### **LangChain vs Manual Dataset** (`langchain_vs_manual_dataset.json`)  
Designed to showcase discussion vs linear workflow:
- **Conflict resolution**: Cases where departments disagree
- **Consensus building**: Complex decisions requiring negotiation
- **Expert disagreement**: Technical vs business vs user perspectives
- **Ground truth**: Only positive, negative, neutral

### **Simple Cases Dataset** (`simple_cases_dataset.json`)
Clear-cut cases where single agent should excel:
- **Obvious sentiment**: No conflicting signals
- **Straightforward language**: Clear positive/negative tone
- **No trade-offs**: Single clear outcome
- **Ground truth**: Simple positive, negative, neutral 