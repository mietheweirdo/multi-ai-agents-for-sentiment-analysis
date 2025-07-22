# Installation Guide

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 2GB available memory
- **Storage**: 100MB for dependencies + data storage
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 4GB+ available memory
- **Storage**: 1GB+ for large datasets
- **CPU**: Multi-core processor for faster processing

## Installation Methods

### Method 1: Standard Installation (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd test_thesis
   ```

2. **Create virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install minimal dependencies**:
   ```bash
   pip install -r requirements_preprocessing.txt
   ```

### Method 2: Full Feature Installation

For complete functionality including Jupyter notebook support:

```bash
pip install -r requirements.txt
```

### Method 3: Docker Installation

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements_preprocessing.txt .
   RUN pip install -r requirements_preprocessing.txt

   COPY . .
   EXPOSE 8888

   CMD ["python", "advanced_preprocessing.py"]
   ```

2. **Build and run**:
   ```bash
   docker build -t llm-preprocessor .
   docker run -v $(pwd)/data:/app/data llm-preprocessor
   ```

## Dependencies

### Core Dependencies (requirements_preprocessing.txt)
```
pandas>=1.3.0          # Data manipulation
numpy>=1.21.0           # Numerical operations
unicodedata2>=14.0.0    # Unicode normalization
```

### Full Dependencies (requirements.txt)
- **Data Processing**: pandas, numpy, scipy
- **Web Scraping**: requests, beautifulsoup4, selenium
- **Text Processing**: langdetect, nltk
- **Machine Learning**: scikit-learn, transformers
- **Visualization**: matplotlib, seaborn
- **Jupyter**: notebook, ipywidgets
- **API Access**: youtube-transcript-api, tweepy

## Platform-Specific Instructions

### Windows

1. **Install Python** from [python.org](https://www.python.org/downloads/)
2. **Open Command Prompt** as Administrator
3. **Verify installation**:
   ```cmd
   python --version
   pip --version
   ```
4. **Follow standard installation** steps above

**Common Windows Issues:**
- **Long path names**: Enable long path support in Windows
- **Permission errors**: Run Command Prompt as Administrator
- **SSL certificates**: Update certificates with `pip install --upgrade certifi`

### macOS

1. **Install Python** using Homebrew (recommended):
   ```bash
   brew install python
   ```
   Or download from [python.org](https://www.python.org/downloads/)

2. **Install Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

3. **Follow standard installation** steps above

**Common macOS Issues:**
- **Permission denied**: Use `sudo` for system-wide installations
- **Certificate issues**: Update certificates with `pip install --upgrade certifi`
- **M1/M2 compatibility**: Use Python 3.9+ for best compatibility

### Linux (Ubuntu/Debian)

1. **Update system packages**:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python and pip**:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Install build essentials** (if needed):
   ```bash
   sudo apt install build-essential python3-dev
   ```

4. **Follow standard installation** steps above

**Common Linux Issues:**
- **Missing headers**: Install `python3-dev` package
- **Permission errors**: Use virtual environments instead of system Python
- **SSL issues**: Update CA certificates with `sudo apt update ca-certificates`

## Verification

### Test Installation

Create a test script to verify everything is working:

```python
# test_installation.py
try:
    from advanced_preprocessing import AgentReadyPreprocessor, PreprocessingConfig
    import pandas as pd
    import numpy as np
    print("✅ All core dependencies imported successfully")
    
    # Test basic functionality
    config = PreprocessingConfig()
    preprocessor = AgentReadyPreprocessor(config)
    print("✅ Preprocessor initialized successfully")
    
    # Test PII redaction
    test_text = "Contact me at test@example.com or call 0123456789. Rating: 8.5/10"
    redacted = preprocessor.redact_pii(test_text)
    print(f"✅ PII redaction working: {redacted}")
    
    print("\n🎉 Installation verified successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check your installation and dependencies")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check the installation guide")
```

Run the test:
```bash
python test_installation.py
```

### Expected Output

```
✅ All core dependencies imported successfully
✅ Preprocessor initialized successfully
✅ PII redaction working: Contact me at [EMAIL_REDACTED] or call [PHONE_VN_REDACTED]. Rating: 8.5/10

🎉 Installation verified successfully!
```

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
```bash
ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Install missing dependencies
```bash
pip install pandas numpy
```

#### 2. Permission Denied
```bash
PermissionError: [Errno 13] Permission denied
```
**Solution**: Use virtual environment or user installation
```bash
pip install --user -r requirements_preprocessing.txt
```

#### 3. SSL Certificate Errors
```bash
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution**: Update certificates
```bash
pip install --upgrade certifi
```

#### 4. Virtual Environment Issues
```bash
'venv' is not recognized as an internal or external command
```
**Solution**: Use full Python path
```bash
python -m venv venv
```

#### 5. Memory Errors with Large Datasets
```bash
MemoryError: Unable to allocate array
```
**Solution**: Process in smaller batches or increase system memory

### Getting Help

1. **Check error logs**: Look for detailed error messages
2. **Verify Python version**: Ensure Python 3.8+
3. **Update pip**: `pip install --upgrade pip`
4. **Clear pip cache**: `pip cache purge`
5. **Reinstall dependencies**: `pip uninstall -r requirements.txt && pip install -r requirements.txt`

### Performance Optimization

#### For Large Datasets
```python
# Adjust configuration for better performance
config = PreprocessingConfig(
    similarity_threshold=0.90,  # Higher threshold = faster processing
    ngram_size=2,              # Smaller n-grams = faster processing
    enable_pii_redaction=False  # Disable if not needed
)
```

#### Memory Management
```python
import gc
import psutil

# Monitor memory usage
def check_memory():
    process = psutil.Process()
    print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")

# Force garbage collection
gc.collect()
```

## Next Steps

After successful installation:

1. **Read the [README.md](README.md)** for project overview
2. **Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)** for detailed API reference
3. **Run the example notebook**: `jupyter notebook agent_ready_preprocessing.ipynb`
4. **Process your own data** using the provided scripts
5. **Integrate with your LLM pipeline** using the agent-ready output

## Support

If you encounter issues not covered in this guide:

1. **Check existing GitHub issues**
2. **Search the documentation**
3. **Create a new issue** with:
   - Your operating system and Python version
   - Complete error message
   - Steps to reproduce the problem
   - Your configuration and data format

---

*Installation guide last updated: June 30, 2025*
