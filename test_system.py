"""
Quick test script to verify Poetry installation and basic functionality
"""

import sys
import os

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import fastapi
        print(f"✓ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"✗ Uvicorn: {e}")
        return False
    
    try:
        import streamlit
        print(f"✓ Streamlit: {streamlit.__version__}")
    except ImportError as e:
        print(f"✗ Streamlit: {e}")
        return False
    
    try:
        import requests
        print(f"✓ Requests: {requests.__version__}")
    except ImportError as e:
        print(f"✗ Requests: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv: OK")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    try:
        import pydantic
        print(f"✓ Pydantic: {pydantic.__version__}")
    except ImportError as e:
        print(f"✗ Pydantic: {e}")
        return False
    
    return True

def test_agent_imports():
    """Test that our agent modules can be imported."""
    print("\nTesting agent imports...")
    
    try:
        from agents.sentiment_agents import ProductQualityAgent, CustomerExperienceAgent, UserExperienceAgent, BusinessImpactAgent, TechnicalSpecAgent
        print("✓ All sentiment agents imported successfully")
    except ImportError as e:
        print(f"✗ Sentiment agents: {e}")
        return False
    
    try:
        from agents.enhanced_coordinator import EnhancedCoordinatorAgent
        print("✓ Enhanced coordinator imported successfully")
    except ImportError as e:
        print(f"✗ Enhanced coordinator: {e}")
        return False
    
    try:
        from shared.json_rpc.base import JSONRPCRequest, JSONRPCResponse, JSONRPCError
        print("✓ JSON-RPC base classes imported successfully")
    except ImportError as e:
        print(f"✗ JSON-RPC base: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        print("✓ OpenAI API key is configured")
    else:
        print("⚠ OpenAI API key not configured (tests may fail)")
    
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"✓ OpenAI model: {model}")
    
    ports = [
        ("Quality Agent", os.getenv("QUALITY_AGENT_PORT", 8001)),
        ("Experience Agent", os.getenv("EXPERIENCE_AGENT_PORT", 8002)),
        ("User Experience Agent", os.getenv("USER_EXPERIENCE_AGENT_PORT", 8003)),
        ("Business Agent", os.getenv("BUSINESS_AGENT_PORT", 8004)),
        ("Technical Agent", os.getenv("TECHNICAL_AGENT_PORT", 8005)),
        ("Coordinator Agent", os.getenv("COORDINATOR_AGENT_PORT", 8000))
    ]
    
    for name, port in ports:
        print(f"✓ {name} port: {port}")
    
    return True

def main():
    """Run all tests."""
    print("=== Multi-Agent Sentiment Analysis A2A System Test ===\n")
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test agent imports
    if not test_agent_imports():
        success = False
    
    # Test environment
    if not test_environment():
        success = False
    
    print(f"\n=== Test Results ===")
    if success:
        print("✓ All tests passed! System is ready.")
    else:
        print("✗ Some tests failed. Check the output above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
