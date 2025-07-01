# Simple Evaluation System

Đây là phiên bản đơn giản của hệ thống đánh giá Multi-Agent Sentiment Analysis.

## 🚀 Cách sử dụng

### 1. Chạy đánh giá đầy đủ
```bash
python3 evaluation/simple_evaluation.py
```

### 2. Kết quả
- Hiển thị trực tiếp trên console
- Lưu vào file `evaluation/simple_results.json`

## 📊 So sánh

Hệ thống sẽ so sánh:
- **Single Agent**: Chỉ dùng 1 agent user_experience
- **Multi-Agent**: Dùng 4 agents (quality, experience, user_experience, business)

## 📁 Files

- `simple_evaluation.py` - Script chính
- `labeled_dataset.json` - Dữ liệu test (17 samples)
- `simple_results.json` - Kết quả (tự động tạo)
- `README_simple.md` - File này

## 📈 Metrics

- **Accuracy**: Tỷ lệ dự đoán đúng
- **Processing Time**: Thời gian xử lý
- **Improvement**: Cải thiện của Multi-Agent so với Single Agent

Đơn giản, nhanh gọn, không phức tạp! 🎯 