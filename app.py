# app.py
"""
Multi-Agent Sentiment Analysis Streamlit Orchestrator
A2A-compatible interface following the Cross-Framework POC pattern
"""

import streamlit as st
import requests
import uuid
import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RPC Endpoint URLs
QUALITY_RPC = f"http://localhost:{os.getenv('QUALITY_AGENT_PORT', '8001')}/rpc"
EXPERIENCE_RPC = f"http://localhost:{os.getenv('EXPERIENCE_AGENT_PORT', '8002')}/rpc"
USER_EXPERIENCE_RPC = f"http://localhost:{os.getenv('USER_EXPERIENCE_AGENT_PORT', '8003')}/rpc"
BUSINESS_RPC = f"http://localhost:{os.getenv('BUSINESS_AGENT_PORT', '8004')}/rpc"
TECHNICAL_RPC = f"http://localhost:{os.getenv('TECHNICAL_AGENT_PORT', '8005')}/rpc"
COORDINATOR_RPC = f"http://localhost:{os.getenv('COORDINATOR_AGENT_PORT', '8000')}/rpc"

# Agent endpoint mapping
AGENT_ENDPOINTS = {
    "quality": QUALITY_RPC,
    "experience": EXPERIENCE_RPC,
    "user_experience": USER_EXPERIENCE_RPC,
    "business": BUSINESS_RPC,
    "technical": TECHNICAL_RPC,
    "coordinator": COORDINATOR_RPC
}

def create_rpc_payload(text: str, task_id: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized A2A JSON-RPC payload"""
    if task_id is None:
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

def call_agent_rpc(endpoint: str, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call an agent RPC endpoint and return the response"""
    payload = create_rpc_payload(text, metadata=metadata)
    
    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to call agent: {str(e)}")
        return None

def extract_result_text(response: Dict[str, Any]) -> str:
    """Extract the result text from A2A response"""
    try:
        return response["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
    except (KeyError, IndexError, TypeError):
        return "Error: Invalid response format"

def parse_agent_result(result_text: str) -> Dict[str, Any]:
    """Parse JSON result from agent response"""
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse agent response", "raw": result_text}

# Page configuration
st.set_page_config(
    page_title="🤖 Multi-Agent Sentiment Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🤖 Multi-Agent Sentiment Analysis System")
st.markdown("*A2A-compatible sentiment analysis with specialized agents*")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Product category selection
product_categories = [
    "electronics", "fashion", "home_garden", 
    "beauty_health", "sports_outdoors", "books_media"
]
product_category = st.sidebar.selectbox(
    "Product Category:",
    product_categories,
    index=0,
    help="Select the product category for specialized analysis"
)

# Analysis mode selection
analysis_modes = {
    "🎯 Coordinator (Multi-Agent)": "coordinator",
    "⚡ Individual Agents": "individual",
    "🔄 Sequential Chain": "sequential"
}
analysis_mode = st.sidebar.selectbox(
    "Analysis Mode:",
    list(analysis_modes.keys()),
    index=0,
    help="Choose how to run the sentiment analysis"
)

# Agent selection for individual/sequential modes
if analysis_modes[analysis_mode] != "coordinator":
    st.sidebar.subheader("Agent Selection")
    selected_agents = []
    
    agent_options = {
        "🔧 Quality Agent": "quality",
        "🤝 Experience Agent": "experience", 
        "😊 User Experience Agent": "user_experience",
        "📊 Business Agent": "business",
        "⚙️ Technical Agent": "technical"
    }
    
    for display_name, agent_type in agent_options.items():
        if st.sidebar.checkbox(display_name, value=True, key=f"agent_{agent_type}"):
            selected_agents.append(agent_type)

# Advanced settings
st.sidebar.subheader("Advanced Settings")
max_tokens_per_agent = st.sidebar.slider(
    "Max Tokens per Agent:",
    min_value=50,
    max_value=500,
    value=int(os.getenv("DEFAULT_MAX_TOKENS_PER_AGENT", "150")),
    step=50,
    help="Token limit for each agent analysis"
)

if analysis_modes[analysis_mode] == "coordinator":
    max_tokens_consensus = st.sidebar.slider(
        "Max Tokens for Consensus:",
        min_value=200,
        max_value=1500,
        value=int(os.getenv("DEFAULT_MAX_TOKENS_CONSENSUS", "800")),
        step=100,
        help="Token limit for consensus generation"
    )
    
    max_rounds = st.sidebar.slider(
        "Max Discussion Rounds:",
        min_value=1,
        max_value=5,
        value=int(os.getenv("DEFAULT_MAX_ROUNDS", "2")),
        help="Maximum rounds of agent discussion"
    )

# Main content area
st.markdown("---")

# Text input
review_text = st.text_area(
    "📝 Enter product review text:",
    height=150,
    placeholder="Enter a product review to analyze sentiment, emotions, and business impact...",
    help="Paste or type a product review for sentiment analysis"
)

# Analysis button
if st.button("🚀 Analyze Sentiment", type="primary", use_container_width=True):
    if not review_text.strip():
        st.warning("⚠️ Please enter some review text to analyze.")
    else:
        # Prepare metadata
        metadata = {
            "product_category": product_category,
            "max_tokens": max_tokens_per_agent
        }
        
        if analysis_modes[analysis_mode] == "coordinator":
            # Coordinator mode - single call to coordinator
            metadata.update({
                "agent_types": ["quality", "experience", "user_experience", "business"],
                "max_tokens_consensus": max_tokens_consensus,
                "max_rounds": max_rounds
            })
            
            st.markdown("### 🎯 Coordinator Analysis")
            
            with st.spinner("Coordinating multi-agent analysis..."):
                response = call_agent_rpc(COORDINATOR_RPC, review_text, metadata)
            
            if response and "result" in response:
                result_text = extract_result_text(response)
                coordinator_result = parse_agent_result(result_text)
                
                if "error" not in coordinator_result:
                    # Display consensus results
                    consensus = coordinator_result.get("consensus", {})
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Overall Sentiment",
                            consensus.get("overall_sentiment", "unknown").title(),
                            help="Consensus sentiment across all agents"
                        )
                    
                    with col2:
                        confidence = consensus.get("overall_confidence", 0.0)
                        st.metric(
                            "Confidence", 
                            f"{confidence:.2%}",
                            help="Average confidence across agents"
                        )
                    
                    with col3:
                        agreement = consensus.get("agreement_level", "unknown")
                        st.metric(
                            "Agreement Level",
                            agreement.title(),
                            help="Level of agreement between agents"
                        )
                    
                    # Display individual agent analyses
                    st.markdown("#### 🤖 Individual Agent Analyses")
                    agent_analyses = coordinator_result.get("agent_analyses", [])
                    
                    for i, analysis in enumerate(agent_analyses):
                        agent_type = analysis.get("agent_type", "unknown")
                        sentiment = analysis.get("sentiment", "unknown")
                        confidence = analysis.get("confidence", 0.0)
                        reasoning = analysis.get("reasoning", "No reasoning provided")
                        
                        with st.expander(f"🔍 {agent_type.title().replace('_', ' ')} Agent - {sentiment.title()}"):
                            st.write(f"**Confidence:** {confidence:.2%}")
                            st.write(f"**Reasoning:** {reasoning}")
                            
                            emotions = analysis.get("emotions", [])
                            if emotions:
                                st.write(f"**Emotions:** {', '.join(emotions)}")
                            
                            topics = analysis.get("topics", [])
                            if topics:
                                st.write(f"**Topics:** {', '.join(topics)}")
                    
                    # Display consensus insights
                    st.markdown("#### 💡 Key Insights")
                    insights = consensus.get("key_insights", "No insights available")
                    st.info(insights)
                    
                    recommendations = consensus.get("business_recommendations", "No recommendations available")
                    st.markdown("#### 📈 Business Recommendations")
                    st.success(recommendations)
                    
                    # Display metadata
                    with st.expander("📊 Analysis Metadata"):
                        metadata_info = coordinator_result.get("analysis_metadata", {})
                        st.json(metadata_info)
                else:
                    st.error(f"❌ Coordinator analysis failed: {coordinator_result.get('error', 'Unknown error')}")
            else:
                st.error("❌ Failed to get response from coordinator")
                
        elif analysis_modes[analysis_mode] == "individual":
            # Individual agents mode - parallel calls
            st.markdown("### ⚡ Individual Agent Analysis")
            
            if not selected_agents:
                st.warning("⚠️ Please select at least one agent to analyze.")
            else:
                # Create columns for agents
                cols = st.columns(len(selected_agents))
                
                for i, agent_type in enumerate(selected_agents):
                    with cols[i]:
                        st.markdown(f"#### 🤖 {agent_type.title().replace('_', ' ')} Agent")
                        
                        with st.spinner(f"Analyzing with {agent_type} agent..."):
                            endpoint = AGENT_ENDPOINTS[agent_type]
                            response = call_agent_rpc(endpoint, review_text, metadata)
                        
                        if response and "result" in response:
                            result_text = extract_result_text(response)
                            agent_result = parse_agent_result(result_text)
                            
                            if "error" not in agent_result:
                                sentiment = agent_result.get("sentiment", "unknown")
                                confidence = agent_result.get("confidence", 0.0)
                                
                                st.metric("Sentiment", sentiment.title())
                                st.metric("Confidence", f"{confidence:.2%}")
                                
                                reasoning = agent_result.get("reasoning", "No reasoning provided")
                                st.write(f"**Reasoning:** {reasoning}")
                                
                                with st.expander("Details"):
                                    st.json(agent_result)
                            else:
                                st.error(f"❌ Analysis failed: {agent_result.get('error', 'Unknown error')}")
                        else:
                            st.error(f"❌ Failed to get response from {agent_type} agent")
                            
        else:
            # Sequential chain mode - call agents one by one
            st.markdown("### 🔄 Sequential Agent Chain")
            
            if not selected_agents:
                st.warning("⚠️ Please select at least one agent to analyze.")
            else:
                results = []
                
                for i, agent_type in enumerate(selected_agents):
                    st.markdown(f"#### Step {i+1}: 🤖 {agent_type.title().replace('_', ' ')} Agent")
                    
                    with st.spinner(f"Analyzing with {agent_type} agent..."):
                        endpoint = AGENT_ENDPOINTS[agent_type]
                        response = call_agent_rpc(endpoint, review_text, metadata)
                    
                    if response and "result" in response:
                        result_text = extract_result_text(response)
                        agent_result = parse_agent_result(result_text)
                        
                        if "error" not in agent_result:
                            results.append({
                                "agent_type": agent_type,
                                "result": agent_result
                            })
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                sentiment = agent_result.get("sentiment", "unknown")
                                confidence = agent_result.get("confidence", 0.0)
                                st.metric("Sentiment", sentiment.title())
                                st.metric("Confidence", f"{confidence:.2%}")
                            
                            with col2:
                                reasoning = agent_result.get("reasoning", "No reasoning provided")
                                st.write(f"**Reasoning:** {reasoning}")
                                
                                emotions = agent_result.get("emotions", [])
                                if emotions:
                                    st.write(f"**Emotions:** {', '.join(emotions)}")
                        else:
                            st.error(f"❌ Analysis failed: {agent_result.get('error', 'Unknown error')}")
                            break
                    else:
                        st.error(f"❌ Failed to get response from {agent_type} agent")
                        break
                
                # Summary of sequential results
                if results:
                    st.markdown("#### 📊 Sequential Analysis Summary")
                    
                    sentiments = [r["result"].get("sentiment", "unknown") for r in results]
                    avg_confidence = sum(r["result"].get("confidence", 0.0) for r in results) / len(results)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        from collections import Counter
                        sentiment_counts = Counter(sentiments)
                        most_common_sentiment = sentiment_counts.most_common(1)[0][0]
                        st.metric("Majority Sentiment", most_common_sentiment.title())
                    
                    with col2:
                        st.metric("Average Confidence", f"{avg_confidence:.2%}")
                    
                    with st.expander("Complete Sequential Results"):
                        st.json(results)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🤖 Multi-Agent Sentiment Analysis System | A2A Protocol Compatible
    </div>
    """,
    unsafe_allow_html=True
)
