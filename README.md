# Hệ thống Multi-Agent AI cho Phân tích Cảm xúc Khách hàng

**Multi-Agent AI System for Customer Sentiment Analysis**

🤖 **Kiến trúc 3 tầng** | 🔗 **A2A Protocol** | 🎯 **Phân tích thời gian thực** | 📊 **Pipeline dữ liệu động**

---

## 📋 **Giới thiệu**

Hệ thống phân tích cảm xúc khách hàng sử dụng kiến trúc multi-agent AI với 3 tầng chuyên biệt:

- **Tầng 1 - Các Agent Chuyên môn**: Quality, Experience, UX, Business, Technical
- **Tầng 2 - Master Analyst**: Tổng hợp và phân tích từ các department
- **Tầng 3 - Business Advisor**: Đưa ra khuyến nghị kinh doanh cụ thể

### **Tính năng chính:**
- ✅ Thu thập dữ liệu từ YouTube và Tiki
- ✅ Phân tích cảm xúc theo từng khía cạnh chuyên môn
- ✅ Giao tiếp agent qua JSON-RPC 2.0 (A2A Protocol)
- ✅ Giao diện web Streamlit trực quan
- ✅ Hỗ trợ nhiều loại sản phẩm (Electronics, Fashion, Beauty, etc.)

---

## 🏗️ **Kiến trúc Hệ thống**

```mermaid
graph TD
    A[Input Review] --> B[Department Agents Layer]
    B --> C[Quality Agent]
    B --> D[Experience Agent]
    B --> E[UX Agent]
    B --> F[Business Agent]
    B --> G[Technical Agent]
    
    C --> H[Master Analyst]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I[Business Advisor]
    I --> J[Final Recommendations]
    
    style A fill:#e1f5fe
    style H fill:#f3e5f5
    style J fill:#e8f5e8
```

---

## 🚀 **Quick Start**

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
```bash
# Tạo file .env
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Tạo file config.json và thêm vào nội dụng:
{
  "api_key": "your_openai_api_key",
  "model_name": "gpt-4o-mini",
  "youtube_api_key": "your_youtube_api_key",
  "youtube_max_videos": 5,
  "youtube_max_comments": 30
}

```

### 3. Chọn cách chạy hệ thống

#### **🤖 Option B: LangGraph Auto-Scraping (Recommended)**
```bash
# Chạy LangGraph với auto scraping từ YouTube + Tiki
python demo_langchain_system.py
```
- ✅ Tự động scrape dữ liệu theo keyword
- ✅ LangGraph discussion-based workflow
- ✅ Phân tích từng review riêng lẻ
- ✅ Business recommendations tự động

#### **🎯 Option A: Multi-Agent Manual**
```bash
# Chạy 3-layer workflow với input thủ công
python demo_enhanced_system.py
```
- ✅ Workflow 3 tầng: Department → Master → Business Advisor
- ✅ Test nhiều loại review khác nhau
- ✅ Hiển thị chi tiết disagreement giữa các agent
- ✅ Interactive menu để test các tính năng

#### **📊 Option C: Multi-Review Summary Analysis**
```bash
# Tổng hợp nhiều review → phân tích 1 lần
python demo_langchain_system_summary.py
```
- ✅ Scrape nhiều review cùng lúc
- ✅ Kết hợp tất cả review thành 1 dataset
- ✅ Phân tích tổng thể comprehensive
- ✅ Business insights từ toàn bộ dataset

#### **🌐 Option D: Streamlit Web Interface**
```bash
# Giao diện web trực quan
streamlit run app.py
```
- ✅ UI thân thiện, dễ sử dụng
- ✅ Chọn agent types và product categories
- ✅ Real-time analysis results
- ✅ A2A Protocol compatible

#### **🔗 Option E: A2A Agent Servers**
```bash
# Chạy các agent riêng lẻ (JSON-RPC endpoints)
python scripts/start_agents.py
```
- ✅ Microservice architecture
- ✅ JSON-RPC 2.0 endpoints
- ✅ Scalable agent communication
- ✅ Perfect for integration

---

## 💻 **Cách sử dụng**

### **Streamlit Interface**
1. Mở trình duyệt tại `http://localhost:8501`
2. Chọn loại sản phẩm (Electronics, Fashion, etc.)
3. Nhập review cần phân tích
4. Chọn chế độ phân tích (Coordinator/Individual/Sequential)
5. Xem kết quả phân tích chi tiết

### **A2A Protocol API**
```python
import requests

# Gọi Quality Agent
payload = {
    "jsonrpc": "2.0",
    "id": "test-123",
    "method": "tasks/send",
    "params": {
        "id": "test-123",
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": "Sản phẩm chất lượng tuyệt vời!"}]
        },
        "metadata": {
            "product_category": "electronics",
            "max_tokens": 150
        }
    }
}

response = requests.post("http://localhost:8001/rpc", json=payload)
result = response.json()
```

### **Workflow Manager**
```python
from workflow_manager import MultiAgentWorkflowManager

# Tạo workflow manager
manager = MultiAgentWorkflowManager(
    product_category="electronics",
    max_tokens_per_department=150
)

# Phân tích review
result = manager.run_analysis("Điện thoại tuyệt vời nhưng giao hàng chậm")
print(f"Sentiment: {result['master_analysis']['sentiment']}")
```

---

## 📁 **Cấu trúc Project**

```
multi-ai-agents-for-sentiment-analysis/
├── 📂 agents/                      # Các agent chuyên môn
│   ├── sentiment_agents.py         # Implementation các agent
│   ├── langgraph_coordinator.py    # LangGraph coordinator
│   └── prompts/                    # Agent prompts
├── 📂 data_pipeline/               # Thu thập & xử lý dữ liệu
│   ├── scrapers.py                 # YouTube & Tiki scrapers
│   ├── preprocessor.py             # Text preprocessing
│   └── pipeline.py                 # Data pipeline chính
├── 📂 rpc_servers/                 # A2A JSON-RPC endpoints
│   ├── quality_agent_rpc.py        # Quality agent endpoint
│   ├── experience_agent_rpc.py     # Experience agent endpoint
│   └── coordinator_agent_rpc.py    # Coordinator endpoint
├── 📂 evaluation/                  # Testing & evaluation
├── 📂 scripts/                     # Automation scripts
├── 📄 app.py                       # Streamlit web interface
├── 📄 workflow_manager.py          # Workflow orchestration
└── 📄 config.json                  # System configuration
```

---

## ⚙️ **Configuration**

### **config.json**
```json
{
  "model_name": "gpt-4o-mini",
  "api_key": "your_openai_api_key",
  "youtube_api_key": "your_youtube_api_key",
  "youtube_max_videos": 5,
  "youtube_max_comments": 30
}
```

### **Agent Ports (A2A Mode)**
- Quality Agent: `http://localhost:8001/rpc`
- Experience Agent: `http://localhost:8002/rpc`
- UX Agent: `http://localhost:8003/rpc`
- Business Agent: `http://localhost:8004/rpc`
- Technical Agent: `http://localhost:8005/rpc`
- Coordinator: `http://localhost:8000/rpc`

---

## 🧪 **Development & Testing**

### **Chạy tests**
```bash
# Unit tests
pytest tests/ -v

# Integration tests
python scripts/test_a2a_workflow.py

# Health check
python scripts/start_agents.py --health-check
```

### **Evaluation**
```bash
# Comprehensive evaluation
python evaluation/evaluation_script.py

# Quick test
python evaluation/quick_test.py
```

---

## 🎯 **Loại sản phẩm hỗ trợ**

- **Electronics**: Điện thoại, laptop, đồ điện tử
- **Fashion**: Quần áo, giày dép, phụ kiện
- **Beauty & Health**: Mỹ phẩm, chăm sóc sức khỏe
- **Home & Garden**: Đồ gia dụng, trang trí nhà
- **Sports & Outdoors**: Thể thao, dụng cụ ngoài trời
- **Books & Media**: Sách, phim, âm nhạc

---

## 🔧 **Troubleshooting**

### **Lỗi thường gặp:**
1. **OpenAI API Error**: Kiểm tra API key trong `config.json`
2. **Port conflicts**: Thay đổi port trong `scripts/start_agents.py`
3. **Memory issues**: Giảm `max_tokens` trong config
4. **Slow response**: Kiểm tra kết nối mạng và API limits

### **Debug mode:**
```bash
# Chạy với debug logs
python app.py --debug

# Verbose output
python workflow_manager.py --verbose
```

---

## 📊 **So sánh 3 Approach chính**

### **🎯 Approach A: Multi-Agent Manual**
```bash
python demo_enhanced_system.py
```
**Input**: "Điện thoại iPhone 15 Pro Max chất lượng tuyệt vời, camera siêu đẹp nhưng giá hơi cao và giao hàng chậm"

**Output**:
- **Quality Agent**: Positive (0.85) - "Chất lượng sản phẩm xuất sắc"
- **Experience Agent**: Negative (0.70) - "Giao hàng chậm ảnh hưởng trải nghiệm"
- **UX Agent**: Positive (0.80) - "Người dùng hài lòng với chức năng"
- **Business Agent**: Neutral (0.65) - "Giá cao có thể ảnh hưởng doanh số"
- **Master Analysis**: Positive (0.75) - "Tổng thể tích cực với một số điểm cần cải thiện"
- **Business Recommendations**: "Cải thiện tốc độ giao hàng, xem xét chính sách giá"

### **🤖 Approach B: LangGraph Auto-Scraping**
```bash
python demo_langchain_system.py
```
**Input**: Nhập keyword "iPhone 15" → Auto scrape từ YouTube + Tiki

**Output**:
```
🔍 Found 6 reviews
🔄 Discussion rounds: 2
🤝 Consensus reached: Yes
🎯 Final sentiment: POSITIVE (0.82)
💼 BUSINESS RECOMMENDATIONS: Focus on delivery speed improvement and pricing strategy optimization
⏱️ Processing time: 15.2s
```

### **📊 Approach C: Multi-Review Summary**
```bash
python demo_langchain_system_summary.py
```
**Input**: Nhập keyword "iPhone 15" → Scrape 10 reviews → Combine thành 1 dataset

**Output**:
```
📈 Dataset: 10 customer reviews analyzed
🔄 Discussion rounds: 3
📊 Sentiment Distribution: {'positive': 6, 'neutral': 3, 'negative': 1}
🎯 MASTER ANALYST: POSITIVE (0.78)
💼 COMPREHENSIVE BUSINESS RECOMMENDATIONS:
   • HIGH PRIORITY: Improve delivery logistics (mentioned in 7/10 reviews)
   • MEDIUM PRIORITY: Pricing strategy review (mentioned in 4/10 reviews)
   • LOW PRIORITY: Camera feature enhancement (mentioned in 2/10 reviews)
   • BUSINESS IMPACT: Estimated 15% customer satisfaction increase
📊 Confidence: 0.85
⏱️ Processing time: 32.8s
```

### **🎯 Khi nào dùng approach nào?**
- **Manual (A)**: Phân tích chi tiết 1 review, test tính năng, development
- **Auto-Scraping (B)**: Phân tích nhanh nhiều review riêng lẻ, research sản phẩm
- **Summary (C)**: Phân tích tổng thể thị trường, business intelligence, comprehensive insights

---
