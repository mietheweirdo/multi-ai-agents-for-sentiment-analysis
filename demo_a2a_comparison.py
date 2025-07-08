#!/usr/bin/env python3
"""
Demo script to compare Standard vs A2A communication modes
"""

import requests
import json
import time
from datetime import datetime

def test_conversational_agent(test_message: str, mode: str = "standard"):
    """Test the conversational agent with a product question"""
    
    print(f"\n{'='*60}")
    print(f"🧪 TESTING {mode.upper()} MODE")
    print(f"{'='*60}")
    print(f"📝 Input: {test_message}")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Prepare RPC request
    payload = {
        "jsonrpc": "2.0",
        "id": f"demo-{int(time.time())}",
        "method": "tasks/send",
        "params": {
            "id": f"test-{int(time.time())}",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": test_message}]
            },
            "metadata": {
                "demo_mode": True,
                "test_type": "product_analysis"
            }
        }
    }
    
    try:
        print(f"📡 Calling conversational agent...")
        start_time = time.time()
        
        # Call conversational agent (port 8010)
        response = requests.post(
            "http://localhost:8010/rpc", 
            json=payload,
            timeout=120
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            if "result" in result:
                # Extract response text
                response_text = result["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
                
                print(f"✅ Response received in {duration:.1f}s")
                print(f"\n🤖 Assistant Response:")
                print("-" * 40)
                print(response_text)
                print("-" * 40)
                
                # Extract metadata
                metadata = result["result"].get("metadata", {})
                if metadata:
                    print(f"\n📊 Metadata:")
                    for key, value in metadata.items():
                        print(f"  • {key}: {value}")
                
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


def main():
    """Demo both communication modes"""
    
    print("🚀 Multi-Agent Sentiment Analysis Demo")
    print("Comparing Standard vs A2A Communication Modes")
    
    # Test message
    test_message = "What should I improve about iPhone 14 to make it better?"
    
    print(f"\n📱 Test Query: '{test_message}'")
    print(f"⚡ This will trigger product analysis with review scraping")
    
    # Check which mode is running
    try:
        # Try to reach enhanced A2A coordinator
        health_response = requests.get("http://localhost:8020/health", timeout=5)
        if health_response.status_code == 200:
            a2a_available = True
            coordinator_info = health_response.json()
            print(f"\n🔗 A2A Coordinator detected:")
            print(f"  • Version: {coordinator_info.get('version', 'unknown')}")
            print(f"  • Available agents: {len(coordinator_info.get('available_agents', []))}")
        else:
            a2a_available = False
    except:
        a2a_available = False
    
    # Check standard coordinator
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        standard_available = health_response.status_code == 200
    except:
        standard_available = False
    
    # Check conversational agent
    try:
        health_response = requests.get("http://localhost:8010/health", timeout=5)
        if health_response.status_code == 200:
            conv_available = True
            conv_info = health_response.json()
            use_a2a = conv_info.get("metadata", {}).get("using_a2a_coordinator", False)
        else:
            conv_available = False
            use_a2a = False
    except:
        conv_available = False
        use_a2a = False
    
    print(f"\n🔍 System Status:")
    print(f"  • Conversational Agent: {'✅' if conv_available else '❌'}")
    print(f"  • Standard Coordinator: {'✅' if standard_available else '❌'}")
    print(f"  • A2A Coordinator: {'✅' if a2a_available else '❌'}")
    print(f"  • Current Mode: {'A2A' if use_a2a else 'Standard'}")
    
    if not conv_available:
        print("\n❌ Conversational agent not available!")
        print("Please start the system first:")
        print("  Standard: python scripts/start_agents.py")
        print("  A2A:      python scripts/start_agents.py --a2a")
        return
    
    # Run test
    if use_a2a and a2a_available:
        test_conversational_agent(test_message, "A2A")
        
        print(f"\n🔗 A2A Communication Flow:")
        print(f"  1. 💬 User → Conversational Agent (port 8010)")
        print(f"  2. 🔄 Conversational Agent → Enhanced A2A Coordinator (port 8020)")
        print(f"  3. 📡 A2A Coordinator → Individual Agents via JSON-RPC:")
        print(f"     • Quality Agent (port 8001)")
        print(f"     • Experience Agent (port 8002)")
        print(f"     • User Experience Agent (port 8003)")
        print(f"     • Business Agent (port 8004)")
        print(f"  4. 🧠 A2A Coordinator → Combines results")
        print(f"  5. 🤖 Human-formatted response → User")
        
    else:
        test_conversational_agent(test_message, "Standard")
        
        print(f"\n⚙️  Standard Communication Flow:")
        print(f"  1. 💬 User → Conversational Agent (port 8010)")
        print(f"  2. 🔄 Conversational Agent → Standard Coordinator (port 8000)")
        print(f"  3. 📞 Standard Coordinator → Direct function calls to agents")
        print(f"  4. 🧠 Standard Coordinator → Combines results")
        print(f"  5. 🤖 Human-formatted response → User")
    
    print(f"\n💡 To switch modes:")
    print(f"  • Stop current system: python scripts/start_agents.py --stop")
    if use_a2a:
        print(f"  • Start standard mode: python scripts/start_agents.py")
    else:
        print(f"  • Start A2A mode: python scripts/start_agents.py --a2a")
    
    print(f"\n🎯 Key Differences:")
    print(f"  • Standard: Faster, direct function calls")
    print(f"  • A2A: True agent-to-agent via JSON-RPC, more scalable")


if __name__ == "__main__":
    main() 