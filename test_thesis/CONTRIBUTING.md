# Contributing Guidelines

Thank you for your interest in contributing to the LLM-Ready Social Media Sentiment Analysis Preprocessing Pipeline! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new functionality
- **🔧 Code Contributions**: Submit bug fixes and new features  
- **📚 Documentation**: Improve guides, API docs, and examples
- **🧪 Testing**: Add test cases and improve coverage
- **🌍 Translations**: Help with internationalization

## 🚀 Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/repository-name.git
   cd repository-name
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```
5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Dependencies

For development, you'll need additional packages:
```bash
pip install pytest pytest-cov black flake8 mypy pre-commit
```

## 📝 Code Standards

### Python Style Guide

We follow **PEP 8** with some additional guidelines:

- **Line length**: Maximum 88 characters (Black formatter)
- **Imports**: Use absolute imports, sort with `isort`
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Required for all public functions

### Code Formatting

We use **Black** for code formatting:
```bash
black .
```

### Linting

We use **flake8** for linting:
```bash
flake8 . --max-line-length=88 --extend-ignore=E203,W503
```

### Type Checking

We use **mypy** for type checking:
```bash
mypy --ignore-missing-imports .
```

### Example Code Style

```python
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ExampleProcessor:
    """Example processor following project standards.
    
    This class demonstrates the coding standards used in this project.
    
    Args:
        config: Configuration object for the processor
        enable_logging: Whether to enable debug logging
        
    Attributes:
        config: The configuration object
        stats: Processing statistics dictionary
    """
    
    def __init__(self, config: Dict[str, Any], enable_logging: bool = True) -> None:
        self.config = config
        self.stats: Dict[str, int] = {}
        
        if enable_logging:
            logger.info("ExampleProcessor initialized")
    
    def process_items(self, items: List[str]) -> List[Dict[str, Any]]:
        """Process a list of text items.
        
        Args:
            items: List of text strings to process
            
        Returns:
            List of processed item dictionaries
            
        Raises:
            ValueError: If items list is empty
        """
        if not items:
            raise ValueError("Items list cannot be empty")
        
        processed_items = []
        for item in items:
            processed_item = self._process_single_item(item)
            if processed_item:
                processed_items.append(processed_item)
        
        self.stats["processed_count"] = len(processed_items)
        return processed_items
    
    def _process_single_item(self, item: str) -> Optional[Dict[str, Any]]:
        """Process a single text item (private method)."""
        if len(item.strip()) < 5:
            return None
        
        return {
            "original": item,
            "processed": item.strip().lower(),
            "length": len(item)
        }
```

## 🧪 Testing

### Test Structure

Tests should be organized in the `tests/` directory:
```
tests/
├── __init__.py
├── test_preprocessing.py
├── test_quality_filter.py
├── test_pii_redaction.py
└── fixtures/
    ├── sample_tiki_data.json
    └── sample_youtube_data.json
```

### Writing Tests

Use **pytest** for testing:

```python
import pytest
from advanced_preprocessing import AgentReadyPreprocessor, PreprocessingConfig


class TestAgentReadyPreprocessor:
    """Test cases for AgentReadyPreprocessor."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PreprocessingConfig(
            min_text_length=5,
            max_text_length=100,
            enable_pii_redaction=True
        )
    
    @pytest.fixture
    def preprocessor(self, config):
        """Create preprocessor instance."""
        return AgentReadyPreprocessor(config)
    
    def test_pii_redaction_preserves_ratings(self, preprocessor):
        """Test that ratings are preserved during PII redaction."""
        text = "Product rating: 8.5/10, contact: test@example.com"
        result = preprocessor.redact_pii(text)
        
        assert "8.5/10" in result
        assert "test@example.com" not in result
        assert "[EMAIL_REDACTED]" in result
    
    def test_quality_filter_length_validation(self, preprocessor):
        """Test quality filter for minimum length."""
        short_text = "Hi"
        passed, reason = preprocessor.quality_filter(short_text, {})
        
        assert not passed
        assert reason == "too_short"
    
    @pytest.mark.parametrize("text,expected_lang", [
        ("Sản phẩm tốt", "vi"),
        ("Good product", "en"),
        ("Product tốt", "mixed")
    ])
    def test_language_detection(self, preprocessor, text, expected_lang):
        """Test language detection accuracy."""
        language, confidence = preprocessor.detect_language(text)
        assert language == expected_lang
        assert 0.0 <= confidence <= 1.0
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_preprocessing.py

# Run tests with verbose output
pytest -v
```

### Test Coverage

Maintain **minimum 90% test coverage**:
```bash
pytest --cov=. --cov-report=term-missing --cov-fail-under=90
```

## 📚 Documentation

### Docstring Standards

Use **Google-style docstrings**:

```python
def process_text(text: str, language: str = "auto") -> Dict[str, Any]:
    """Process text with language-specific handling.
    
    This function applies preprocessing steps based on the detected
    or specified language.
    
    Args:
        text: The input text to process
        language: Language code ('vi', 'en', or 'auto' for detection)
        
    Returns:
        Dictionary containing:
            - 'processed_text': The cleaned text
            - 'language': Detected or specified language
            - 'confidence': Language detection confidence (0.0-1.0)
            
    Raises:
        ValueError: If text is empty or language code is invalid
        
    Examples:
        >>> result = process_text("Sản phẩm tốt", "vi")
        >>> result['language']
        'vi'
        
        >>> result = process_text("Good product")
        >>> result['processed_text']
        'Good product'
    """
```

### README Updates

When adding new features, update:
- **Feature list** in main README
- **Usage examples** with new functionality
- **Configuration options** if applicable
- **Performance metrics** if changed

## 🔧 Development Workflow

### Branching Strategy

We use **Git Flow** branching model:

- **main**: Production-ready code
- **develop**: Development branch
- **feature/**: New features (`feature/add-batch-processing`)
- **hotfix/**: Critical bug fixes (`hotfix/fix-memory-leak`)
- **release/**: Release preparation (`release/v2.1.0`)

### Commit Messages

Use **Conventional Commits** format:

```bash
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(preprocessing): add batch processing support
fix(pii): preserve ratings during phone number redaction
docs(api): update language detection examples
test(quality): add edge cases for text filtering
```

### Pull Request Process

1. **Update** your feature branch:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature
   git rebase develop
   ```

2. **Run all checks**:
   ```bash
   black .
   flake8 .
   mypy .
   pytest --cov=. --cov-fail-under=90
   ```

3. **Push** your branch:
   ```bash
   git push origin feature/your-feature
   ```

4. **Create Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Test results and coverage
   - Screenshots (if UI changes)
   - Breaking changes documentation

5. **Address review feedback**
6. **Squash and merge** after approval

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Test coverage maintained above 90%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors
```

## 🐛 Bug Reports

### Before Submitting

1. **Search existing issues** for similar problems
2. **Check documentation** for known limitations
3. **Test with latest version**
4. **Prepare minimal reproduction example**

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce the behavior:
1. Configure with settings '...'
2. Process data file '...'
3. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g. Windows 10, macOS 12.1, Ubuntu 20.04]
- Python version: [e.g. 3.9.7]
- Package version: [e.g. 2.0.1]

**Data Sample**
Minimal data sample that reproduces the issue (anonymized)

**Error Logs**
Complete error message and stack trace
```

## ✨ Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Problem Solved**
What problem does this feature solve?

**Proposed Solution**
How would you like this feature to work?

**Alternatives Considered**
Any alternative solutions or features considered?

**Additional Context**
Any other context about the feature request
```

## 🌍 Internationalization

### Adding Language Support

To add support for a new language:

1. **Add language detection** patterns
2. **Create abbreviation dictionary**
3. **Add test cases** with sample data
4. **Update documentation** with language code

Example for adding Spanish support:

```python
# In _load_spanish_abbreviations method
def _load_spanish_abbreviations(self) -> Dict[str, str]:
    return {
        'q': 'que',
        'pq': 'porque',
        'tb': 'también',
        # ... more abbreviations
    }

# In detect_language method
spanish_words = ['que', 'para', 'con', 'una', 'muy', 'producto']
spanish_word_count = sum(1 for word in spanish_words if word in text_lower)
```

## 📊 Performance Guidelines

### Benchmarking

When making performance-related changes:

1. **Benchmark before** changes
2. **Profile** the code to identify bottlenecks
3. **Measure** improvement
4. **Update** performance metrics in documentation

```python
import time
import cProfile

def benchmark_preprocessing():
    start_time = time.time()
    # Your preprocessing code here
    end_time = time.time()
    
    print(f"Processing time: {end_time - start_time:.2f} seconds")

# Profile with cProfile
cProfile.run('benchmark_preprocessing()')
```

### Memory Optimization

- Use generators for large datasets
- Implement batch processing
- Clear unused variables
- Monitor memory usage

## 🏆 Recognition

Contributors will be recognized in:

- **Contributors section** of README
- **Release notes** for significant contributions
- **GitHub contributors** page
- **Special mentions** in documentation

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Code Review**: Pull request discussions

### Mentorship

New contributors can get help with:
- Understanding the codebase
- Setting up development environment
- Writing tests and documentation
- Code review process

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different opinions and approaches

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Unprofessional conduct

### Enforcement

Issues can be reported to project maintainers. All complaints will be reviewed and investigated promptly and fairly.

---

**Thank you for contributing to making LLM data preprocessing better for everyone!** 🚀

*Contributing guidelines last updated: June 30, 2025*
