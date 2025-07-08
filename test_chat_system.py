#!/usr/bin/env python3
"""
Test script for the new conversational chat system
Tests both general chat and product analysis functionality
"""

import requests
import json
import uuid
import time
from typing import Dict, Any

# Test configuration
CONVERSATIONAL_RPC = "http://localhost:8010/rpc"

def create_test_payload(message: str) -> Dict[str, Any]:
    """Create test payload for conversational agent"""
    task_id = str(uuid.uuid4())
    
    return {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": "tasks/send",
        "params": {
            "id": task_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}]
            },
            "metadata": {
                "conversation_id": "test_session",
                "user_id": "test_user"
            }
        }
    }

def test_message(message: str, expected_type: str = None) -> bool:
    """Test a single message"""
    print(f"\n🔍 Testing: '{message}'")
    print("-" * 50)
    
    try:
        payload = create_test_payload(message)
        response = requests.post(CONVERSATIONAL_RPC, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if "result" in result:
                # Extract response text
                response_text = result["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
                metadata = result["result"].get("metadata", {})
                response_type = metadata.get("response_type", "unknown")
                
                print(f"✅ Response Type: {response_type}")
                print(f"📝 Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                
                if expected_type and expected_type not in response_type:
                    print(f"⚠️  Expected type '{expected_type}' but got '{response_type}'")
                    return False
                
                return True
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_health_check() -> bool:
    """Test agent health"""
    try:
        response = requests.get("http://localhost:8010/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Agent Health: {health_data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check exception: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀" * 60)
    print("🚀 CONVERSATIONAL CHAT SYSTEM TEST")
    print("🚀" * 60)
    
    # Test 1: Health Check
    print("\n📋 Test 1: Health Check")
    if not test_health_check():
        print("❌ Health check failed. Is the conversational agent running?")
        print("   Run: python scripts/start_agents.py")
        return
    
    # Test 2: General Chat
    print("\n📋 Test 2: General Chat")
    general_tests = [
        ("What time is it?", "direct_response"),
        ("Hello, how are you?", "llm_response"),
        ("Tell me about business strategy", "llm_response")
    ]
    
    general_passed = 0
    for message, expected_type in general_tests:
        if test_message(message, expected_type):
            general_passed += 1
        time.sleep(1)  # Rate limiting
    
    print(f"\n🎯 General Chat Results: {general_passed}/{len(general_tests)} passed")
    
    # Test 3: Product Analysis (might take longer)
    print("\n📋 Test 3: Product Analysis")
    product_tests = [
        ("What should I improve for iPhone 14?", "product_analysis"),
        ("How can I make Samsung Galaxy better?", "product_analysis"),
        ("Give me recommendations for Oppo A93", "product_analysis")
    ]
    
    product_passed = 0
    for message, expected_type in product_tests:
        print(f"\n⏳ This may take 30-60 seconds for scraping and analysis...")
        if test_message(message, expected_type):
            product_passed += 1
        time.sleep(2)  # Longer delay for product analysis
    
    print(f"\n🎯 Product Analysis Results: {product_passed}/{len(product_tests)} passed")
    
    # Test 4: Clarification Handling
    print("\n📋 Test 4: Clarification Handling")
    clarification_tests = [
        ("How can I improve this product?", "clarification"),
        ("What should I do to make it better?", "clarification")
    ]
    
    clarification_passed = 0
    for message, expected_type in clarification_tests:
        if test_message(message, expected_type):
            clarification_passed += 1
        time.sleep(1)
    
    print(f"\n🎯 Clarification Results: {clarification_passed}/{len(clarification_tests)} passed")
    
    # Summary
    total_tests = len(general_tests) + len(product_tests) + len(clarification_tests)
    total_passed = general_passed + product_passed + clarification_passed
    
    print(f"\n{'='*60}")
    print(f"📊 OVERALL TEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Your conversational chat system is working perfectly!")
        print("\n🚀 Next steps:")
        print("   1. Start the full system: python scripts/start_agents.py")
        print("   2. Launch chat interface: streamlit run app.py")
        print("   3. Try asking: 'What should I improve for iPhone 14?'")
    else:
        print(f"\n⚠️  Some tests failed. Please check the agent logs and configuration.")
        
        if product_passed == 0:
            print("\n💡 If product analysis failed, check:")
            print("   - Coordinator agent is running (port 8000)")
            print("   - Data pipeline is installed and working")
            print("   - OpenAI API key is configured")

if __name__ == "__main__":
    main() 