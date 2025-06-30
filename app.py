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

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Multi-Agent Sentiment Analysis",
        page_icon="robot",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title("Multi-Agent Sentiment Analysis System")
    st.markdown("*An advanced sentiment analysis system using specialized AI agents*")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Product category selection
    product_categories = {
        "Electronics": "electronics",
        "Fashion": "fashion", 
        "Home & Garden": "home_garden",
        "Beauty & Health": "beauty_health",
        "Sports & Outdoors": "sports_outdoors",
        "Books & Media": "books_media"
    }
    
    selected_category = st.sidebar.selectbox(
        "Select Product Category:",
        list(product_categories.keys()),
        index=0
    )
    product_category = product_categories[selected_category]
    
    # Analysis mode selection
    analysis_modes = {
        "Coordinator (Multi-Agent)": "coordinator",
        "Individual Agents": "individual",
        "Sequential Analysis": "sequential"
    }
    
    analysis_mode = st.sidebar.selectbox(
        "Analysis Mode:",
        list(analysis_modes.keys()),
        index=0
    )
    
    mode = analysis_modes[analysis_mode]
    
    # Agent selection (for individual/sequential modes)
    if mode in ["individual", "sequential"]:
        available_agents = {
            "Quality Agent": "quality",
            "Experience Agent": "experience",
            "User Experience Agent": "user_experience",
            "Business Agent": "business",
            "Technical Agent": "technical"
        }
        
        selected_agents = st.sidebar.multiselect(
            "Select Agents:",
            list(available_agents.keys()),
            default=["Quality Agent", "Experience Agent"]
        )
        
        agent_types = [available_agents[agent] for agent in selected_agents]
    else:
        agent_types = ["quality", "experience", "user_experience", "business"]
    
    # Token limit configuration
    max_tokens = st.sidebar.slider(
        "Max Tokens per Agent:",
        min_value=50,
        max_value=500,
        value=300,
        step=25,
        help="Higher values provide more detailed analysis but cost more"
    )
    
    # Main content area
    st.markdown("### Analysis Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Product Category:**", selected_category)
        st.write("**Analysis Mode:**", analysis_mode)
    
    with col2:
        st.write("**Max Tokens:**", max_tokens)
        if mode != "coordinator":
            st.write("**Selected Agents:**", len(agent_types))
    
    # Review input
    st.markdown("### Product Review Analysis")
    
    review_text = st.text_area(
        "Enter product review text:",
        height=150,
        placeholder="Enter the product review you want to analyze..."
    )
    
    # Analysis button
    if st.button("Analyze Sentiment", type="primary", use_container_width=True):
        if not review_text.strip():
            st.warning("Please enter some review text to analyze.")
        else:
            if mode == "coordinator":
                # Coordinator mode
                with st.spinner("Running multi-agent analysis..."):
                    coordinator_result = run_coordinator_analysis(
                        review_text, product_category, agent_types, max_tokens
                    )
                
                if coordinator_result and "consensus" in coordinator_result:
                    st.markdown("### Coordinator Analysis")
                    
                    # Display consensus results
                    consensus = coordinator_result["consensus"]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        sentiment = consensus.get("overall_sentiment", "Unknown")
                        sentiment_color = get_sentiment_color(sentiment)
                        st.markdown(f"**Overall Sentiment:** ::{sentiment_color}[{sentiment.upper()}]")
                    
                    with col2:
                        confidence = consensus.get("overall_confidence", 0.0)
                        st.markdown(f"**Confidence:** {confidence:.2%}")
                        st.progress(confidence)
                    
                    with col3:
                        agreement = consensus.get("agreement_level", "Unknown")
                        st.markdown(f"**Agreement Level:** {agreement}")
                    
                    # Reasoning
                    if "reasoning" in consensus:
                        st.markdown("**Consensus Reasoning:**")
                        st.info(consensus["reasoning"])
                    
                    # Key insights
                    if "key_insights" in consensus:
                        st.markdown("**Key Insights:**")
                        insights = consensus["key_insights"]
                        if isinstance(insights, list):
                            for insight in insights:
                                st.write(f"• {insight}")
                        else:
                            st.write(f"• {insights}")
                    
                    # Individual agent analyses
                    if "agent_analyses" in coordinator_result:
                        st.markdown("#### Individual Agent Analyses")
                        
                        for analysis in coordinator_result["agent_analyses"]:
                            agent_type = analysis.get("agent_type", "Unknown")
                            sentiment = analysis.get("sentiment", "Unknown")
                            confidence = analysis.get("confidence", 0.0)
                            reasoning = analysis.get("reasoning", "No reasoning provided")
                            
                            with st.expander(f"{agent_type.title().replace('_', ' ')} Agent - {sentiment.title()}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Sentiment:**", sentiment.upper())
                                    st.write("**Confidence:**", f"{confidence:.2%}")
                                
                                with col2:
                                    emotions = analysis.get("emotions", [])
                                    if emotions:
                                        st.write("**Emotions:**", ", ".join(emotions))
                                
                                st.write("**Reasoning:**")
                                st.write(reasoning)
                    
                    # Key insights section
                    st.markdown("#### Key Insights")
                    if "key_insights" in consensus:
                        st.write(consensus["key_insights"])
                    
                    # Business recommendations
                    st.markdown("#### Business Recommendations")
                    if "business_recommendations" in consensus:
                        st.write(consensus["business_recommendations"])
                    
                    # Analysis metadata
                    with st.expander("Analysis Metadata"):
                        metadata = coordinator_result.get("analysis_metadata", {})
                        st.json(metadata)
                
                elif coordinator_result and "error" in coordinator_result:
                    st.error(f"Coordinator analysis failed: {coordinator_result.get('error', 'Unknown error')}")
                else:
                    st.error("Failed to get response from coordinator")
            
            elif mode == "individual":
                # Individual agents mode
                if not agent_types:
                    st.warning("Please select at least one agent to analyze.")
                else:
                    st.markdown("### Individual Agent Results")
                    
                    for agent_type in agent_types:
                        with st.spinner(f"Running {agent_type} agent analysis..."):
                            agent_result = run_single_agent_analysis(
                                review_text, agent_type, product_category, max_tokens
                            )
                        
                        st.markdown(f"#### {agent_type.title().replace('_', ' ')} Agent")
                        
                        if agent_result and "sentiment" in agent_result:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                sentiment = agent_result["sentiment"]
                                sentiment_color = get_sentiment_color(sentiment)
                                st.markdown(f"**Sentiment:** ::{sentiment_color}[{sentiment.upper()}]")
                            
                            with col2:
                                confidence = agent_result.get("confidence", 0.0)
                                st.markdown(f"**Confidence:** {confidence:.2%}")
                                st.progress(confidence)
                            
                            with col3:
                                emotions = agent_result.get("emotions", [])
                                if emotions:
                                    st.markdown(f"**Emotions:** {', '.join(emotions[:3])}")
                            
                            # Reasoning
                            reasoning = agent_result.get("reasoning", "No reasoning provided")
                            st.markdown("**Analysis Reasoning:**")
                            st.info(reasoning)
                            
                            # Business impact
                            business_impact = agent_result.get("business_impact", "")
                            if business_impact:
                                st.markdown("**Business Impact:**")
                                st.write(business_impact)
                            
                            # Topics/facets
                            topics = agent_result.get("topics", [])
                            if topics:
                                st.markdown("**Key Topics:**")
                                st.write(", ".join(topics))
                        
                        elif agent_result and "error" in agent_result:
                            st.error(f"Analysis failed: {agent_result.get('error', 'Unknown error')}")
                        else:
                            st.error(f"Failed to get response from {agent_type} agent")
                        
                        st.divider()
            
            elif mode == "sequential":
                # Sequential analysis mode
                if not agent_types:
                    st.warning("Please select at least one agent to analyze.")
                else:
                    st.markdown("### Sequential Analysis")
                    
                    results = []
                    
                    for i, agent_type in enumerate(agent_types):
                        st.markdown(f"#### Step {i+1}: {agent_type.title().replace('_', ' ')} Agent")
                        
                        with st.spinner(f"Running {agent_type} agent analysis..."):
                            agent_result = run_single_agent_analysis(
                                review_text, agent_type, product_category, max_tokens
                            )
                        
                        if agent_result and "sentiment" in agent_result:
                            results.append(agent_result)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                sentiment = agent_result["sentiment"]
                                confidence = agent_result.get("confidence", 0.0)
                                st.metric(
                                    label="Sentiment",
                                    value=sentiment.upper(),
                                    delta=f"{confidence:.2%} confidence"
                                )
                            
                            with col2:
                                reasoning = agent_result.get("reasoning", "No reasoning provided")
                                st.write("**Reasoning:**")
                                st.write(reasoning[:200] + "..." if len(reasoning) > 200 else reasoning)
                        
                        elif agent_result and "error" in agent_result:
                            st.error(f"Analysis failed: {agent_result.get('error', 'Unknown error')}")
                            results.append({"sentiment": "error", "confidence": 0.0})
                        else:
                            st.error(f"Failed to get response from {agent_type} agent")
                            results.append({"sentiment": "error", "confidence": 0.0})
                    
                    # Summary of sequential analysis
                    if results:
                        st.markdown("#### Sequential Analysis Summary")
                        
                        # Calculate summary metrics
                        valid_results = [r for r in results if r["sentiment"] != "error"]
                        
                        if valid_results:
                            sentiments = [r["sentiment"] for r in valid_results]
                            confidences = [r.get("confidence", 0.0) for r in valid_results]
                            
                            # Most common sentiment
                            from collections import Counter
                            sentiment_counts = Counter(sentiments)
                            most_common_sentiment = sentiment_counts.most_common(1)[0][0]
                            
                            # Average confidence
                            avg_confidence = sum(confidences) / len(confidences)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Most Common Sentiment", most_common_sentiment.upper())
                            with col2:
                                st.metric("Average Confidence", f"{avg_confidence:.2%}")
                            with col3:
                                st.metric("Agents Analyzed", len(valid_results))
                            
                            # Sentiment distribution
                            st.markdown("**Sentiment Distribution:**")
                            for sentiment, count in sentiment_counts.items():
                                percentage = (count / len(valid_results)) * 100
                                st.write(f"• {sentiment.title()}: {count} agents ({percentage:.1f}%)")

if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
Multi-Agent Sentiment Analysis System | A2A Protocol Compatible
</div>
""", unsafe_allow_html=True)
