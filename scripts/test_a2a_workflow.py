# scripts/test_a2a_workflow.py
"""
Test script for A2A sentiment analysis workflow
Demonstrates the complete multi-agent sentiment analysis chain
"""

import json
import uuid
import requests
import time
from typing import Dict, Any
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

# Test configuration
TEST_REVIEWS = [
    {
        "text": "This smartphone is absolutely amazing! The camera quality is outstanding and the battery life lasts all day. The user interface is intuitive and the build quality feels premium. However, the delivery took longer than expected and customer service was a bit slow to respond to my questions.",
        "product_category": "electronics",
        "expected_sentiment": "positive"
    },
    {
        "text": "I love this dress! The fabric is soft and comfortable, and the fit is perfect. The color is exactly as shown in the pictures. The delivery was fast and the packaging was beautiful. I've received many compliments when wearing it. Great value for money!",
        "product_category": "fashion", 
        "expected_sentiment": "positive"
    },
    {
        "text": "This coffee maker is a disappointment. The build quality feels cheap and it broke after just 2 weeks of use. The customer service was helpful and offered a replacement, but the new one has the same issues. Not worth the money at all.",
        "product_category": "home_garden",
        "expected_sentiment": "negative"
    }
]

# Agent endpoints
AGENT_ENDPOINTS = {
    "quality": f"http://localhost:{os.getenv('QUALITY_AGENT_PORT', '8001')}/rpc",
    "experience": f"http://localhost:{os.getenv('EXPERIENCE_AGENT_PORT', '8002')}/rpc",
    "user_experience": f"http://localhost:{os.getenv('USER_EXPERIENCE_AGENT_PORT', '8003')}/rpc",
    "business": f"http://localhost:{os.getenv('BUSINESS_AGENT_PORT', '8004')}/rpc",
    "technical": f"http://localhost:{os.getenv('TECHNICAL_AGENT_PORT', '8005')}/rpc",
    "coordinator": f"http://localhost:{os.getenv('COORDINATOR_AGENT_PORT', '8000')}/rpc"
}

def create_a2a_payload(text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create A2A-compliant JSON-RPC payload"""
    task_id = str(uuid.uuid4())
    
    return {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": "tasks/send",
        "params": {
            "id": task_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": text}]
            },
            "metadata": metadata or {}
        }
    }

def call_agent(endpoint: str, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call an A2A agent endpoint"""
    payload = create_a2a_payload(text, metadata)
    
    try:
        print(f"📤 Calling {endpoint}...")
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f" Response received")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f" Request failed: {str(e)}")
        return None

def extract_result_text(response: Dict[str, Any]) -> str:
    """Extract result text from A2A response"""
    try:
        return response["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
    except (KeyError, IndexError, TypeError):
        return None

def parse_agent_result(result_text: str) -> Dict[str, Any]:
    """Parse JSON result from agent response"""
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse agent response", "raw": result_text}

def test_individual_agents():
    """Test individual agent endpoints"""
    print("\n" + "="*60)
    print(" TESTING INDIVIDUAL AGENTS")
    print("="*60)
    
    test_review = TEST_REVIEWS[0]  # Use electronics review
    review_text = test_review["text"]
    metadata = {
        "product_category": test_review["product_category"],
        "max_tokens": 150
    }
    
    print(f"\n Test Review: {review_text[:100]}...")
    print(f" Category: {test_review['product_category']}")
    
    # Test each individual agent
    for agent_name, endpoint in AGENT_ENDPOINTS.items():
        if agent_name == "coordinator":  # Skip coordinator for individual tests
            continue
            
        print(f"\n Testing {agent_name.title().replace('_', ' ')} Agent")
        print("-" * 40)
        
        response = call_agent(endpoint, review_text, metadata)
        
        if response and "result" in response:
            result_text = extract_result_text(response)
            if result_text:
                agent_result = parse_agent_result(result_text)
                
                if "error" not in agent_result:
                    sentiment = agent_result.get("sentiment", "unknown")
                    confidence = agent_result.get("confidence", 0.0)
                    reasoning = agent_result.get("reasoning", "No reasoning")[:100]
                    
                    print(f"  Sentiment: {sentiment}")
                    print(f"  Confidence: {confidence:.2%}")
                    print(f"  Reasoning: {reasoning}...")
                    
                    # Check agent type matches
                    expected_agent_type = agent_name
                    actual_agent_type = agent_result.get("agent_type")
                    if actual_agent_type == expected_agent_type:
                        print(f"   Agent type correct: {actual_agent_type}")
                    else:
                        print(f"   Agent type mismatch: expected {expected_agent_type}, got {actual_agent_type}")
                else:
                    print(f"   Agent error: {agent_result.get('error', 'Unknown error')}")
            else:
                print(f"   Failed to extract result text")
        else:
            print(f"   No valid response from agent")

def test_coordinator_workflow():
    """Test coordinator multi-agent workflow"""
    print("\n" + "="*60)
    print(" TESTING COORDINATOR WORKFLOW")
    print("="*60)
    
    for i, test_review in enumerate(TEST_REVIEWS):
        print(f"\n Test Case {i+1}: {test_review['product_category'].title()} Review")
        print("-" * 50)
        
        review_text = test_review["text"]
        print(f"Review: {review_text[:150]}...")
        
        metadata = {
            "product_category": test_review["product_category"],
            "agent_types": ["quality", "experience", "user_experience", "business"],
            "max_tokens_per_agent": 150,
            "max_tokens_consensus": 800,
            "max_rounds": 2
        }
        
        print(f"Category: {test_review['product_category']}")
        print(f"Expected Sentiment: {test_review['expected_sentiment']}")
        
        start_time = time.time()
        response = call_agent(AGENT_ENDPOINTS["coordinator"], review_text, metadata)
        end_time = time.time()
        
        if response and "result" in response:
            result_text = extract_result_text(response)
            if result_text:
                coordinator_result = parse_agent_result(result_text)
                
                if "error" not in coordinator_result:
                    # Extract consensus
                    consensus = coordinator_result.get("consensus", {})
                    overall_sentiment = consensus.get("overall_sentiment", "unknown")
                    overall_confidence = consensus.get("overall_confidence", 0.0)
                    agreement_level = consensus.get("agreement_level", "unknown")
                    
                    print(f"\n Consensus Results:")
                    print(f"  Overall Sentiment: {overall_sentiment}")
                    print(f"  Confidence: {overall_confidence:.2%}")
                    print(f"  Agreement Level: {agreement_level}")
                    print(f"  Analysis Time: {end_time - start_time:.2f}s")
                    
                    # Check if sentiment matches expectation
                    if overall_sentiment.lower() == test_review["expected_sentiment"].lower():
                        print(f"   Sentiment matches expectation")
                    else:
                        print(f"   Sentiment mismatch: expected {test_review['expected_sentiment']}, got {overall_sentiment}")
                    
                    # Display individual agent results
                    agent_analyses = coordinator_result.get("agent_analyses", [])
                    print(f"\n Individual Agent Results ({len(agent_analyses)} agents):")
                    
                    for analysis in agent_analyses:
                        agent_type = analysis.get("agent_type", "unknown")
                        sentiment = analysis.get("sentiment", "unknown")
                        confidence = analysis.get("confidence", 0.0)
                        
                        print(f"  {agent_type.title().replace('_', ' ')}: {sentiment} ({confidence:.2%})")
                    
                    # Display insights and recommendations
                    insights = consensus.get("key_insights", "No insights available")
                    recommendations = consensus.get("business_recommendations", "No recommendations available")
                    
                    print(f"\n Key Insights:")
                    if isinstance(insights, str):
                        print(f"  {insights[:200]}{'...' if len(insights) > 200 else ''}")
                    else:
                        print(f"  {str(insights)[:200]}{'...' if len(str(insights)) > 200 else ''}")
                    
                    print(f"\n Business Recommendations:")
                    if isinstance(recommendations, str):
                        print(f"  {recommendations[:200]}{'...' if len(recommendations) > 200 else ''}")
                    else:
                        print(f"  {str(recommendations)[:200]}{'...' if len(str(recommendations)) > 200 else ''}")
                    
                    # Metadata
                    metadata_info = coordinator_result.get("analysis_metadata", {})
                    total_agents = metadata_info.get("total_agents", 0)
                    discussion_rounds = metadata_info.get("discussion_rounds", 0)
                    avg_confidence = metadata_info.get("average_confidence", 0.0)
                    
                    print(f"\n Analysis Metadata:")
                    print(f"  Total Agents: {total_agents}")
                    print(f"  Discussion Rounds: {discussion_rounds}")
                    print(f"  Average Confidence: {avg_confidence:.2%}")
                    
                else:
                    print(f" Coordinator error: {coordinator_result.get('error', 'Unknown error')}")
            else:
                print(f" Failed to extract coordinator result")
        else:
            print(f" No valid response from coordinator")

def test_sequential_workflow():
    """Test sequential agent workflow"""
    print("\n" + "="*60)
    print("🔄 TESTING SEQUENTIAL WORKFLOW")
    print("="*60)
    
    test_review = TEST_REVIEWS[0]  # Use electronics review
    review_text = test_review["text"]
    
    metadata = {
        "product_category": test_review["product_category"],
        "max_tokens": 150
    }
    
    print(f"\n Sequential Analysis: {review_text[:100]}...")
    
    # Define sequence of agents
    agent_sequence = ["quality", "experience", "user_experience", "business"]
    results = []
    
    for i, agent_name in enumerate(agent_sequence):
        print(f"\n Step {i+1}: {agent_name.title().replace('_', ' ')} Agent")
        print("-" * 30)
        
        endpoint = AGENT_ENDPOINTS[agent_name]
        response = call_agent(endpoint, review_text, metadata)
        
        if response and "result" in response:
            result_text = extract_result_text(response)
            if result_text:
                agent_result = parse_agent_result(result_text)
                
                if "error" not in agent_result:
                    sentiment = agent_result.get("sentiment", "unknown")
                    confidence = agent_result.get("confidence", 0.0)
                    
                    results.append({
                        "agent": agent_name,
                        "sentiment": sentiment,
                        "confidence": confidence,
                        "result": agent_result
                    })
                    
                    print(f"  Sentiment: {sentiment}")
                    print(f"  Confidence: {confidence:.2%}")
                    print(f"   Analysis complete")
                else:
                    print(f"   Analysis failed: {agent_result.get('error', 'Unknown error')}")
                    break
            else:
                print(f"   Failed to extract result")
                break
        else:
            print(f"   No response from agent")
            break
    
    # Summarize sequential results
    if results:
        print(f"\n Sequential Analysis Summary")
        print("-" * 30)
        
        sentiments = [r["sentiment"] for r in results]
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        
        from collections import Counter
        sentiment_counts = Counter(sentiments)
        majority_sentiment = sentiment_counts.most_common(1)[0][0]
        
        print(f"Agents Completed: {len(results)}/{len(agent_sequence)}")
        print(f"Majority Sentiment: {majority_sentiment}")
        print(f"Average Confidence: {avg_confidence:.2%}")
        print(f"Sentiment Distribution: {dict(sentiment_counts)}")

def test_health_endpoints():
    """Test health endpoints for all agents"""
    print("\n" + "="*60)
    print("🏥 TESTING HEALTH ENDPOINTS")
    print("="*60)
    
    for agent_name, rpc_endpoint in AGENT_ENDPOINTS.items():
        # Convert RPC endpoint to health endpoint
        health_endpoint = rpc_endpoint.replace("/rpc", "/health")
        
        print(f"\n Testing {agent_name.title().replace('_', ' ')} Agent Health")
        print(f"   Endpoint: {health_endpoint}")
        
        try:
            response = requests.get(health_endpoint, timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")
                agent = health_data.get("agent", "unknown")
                version = health_data.get("version", "unknown")
                
                print(f"   Status: {status}")
                print(f"   Agent: {agent}")
                print(f"   Version: {version}")
                print(f"    Health check passed")
            else:
                print(f"    Health check failed: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"    Health check failed: {str(e)}")

def main():
    """Main test runner"""
    print(" A2A SENTIMENT ANALYSIS WORKFLOW TESTER")
    print("="*60)
    print("Testing the complete multi-agent sentiment analysis system")
    print("following the A2A Cross-Framework POC pattern")
    
    # Test health endpoints first
    test_health_endpoints()
    
    # Test individual agents
    test_individual_agents()
    
    # Test coordinator workflow
    test_coordinator_workflow()
    
    # Test sequential workflow
    test_sequential_workflow()
    
    print("\n" + "="*60)
    print(" A2A WORKFLOW TESTING COMPLETE")
    print("="*60)
    print("Review the results above to verify A2A protocol compliance")
    print("and multi-agent sentiment analysis functionality.")

if __name__ == "__main__":
    main()
