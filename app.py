# app.py
"""
Conversational AI Chat Interface
Modern chat interface with intelligent product analysis
"""

import streamlit as st
import requests
import uuid
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Conversational Agent RPC endpoint
CONVERSATIONAL_RPC = f"http://localhost:{os.getenv('CONVERSATIONAL_AGENT_PORT', '8010')}/rpc"

def create_chat_payload(message: str, conversation_id: str = None, user_id: str = "user") -> Dict[str, Any]:
    """Create A2A JSON-RPC payload for conversational agent"""
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
                "conversation_id": conversation_id or "streamlit_session",
                "user_id": user_id
            }
        }
    }

def call_conversational_agent(message: str, conversation_id: str = None) -> Dict[str, Any]:
    """Call the conversational agent and return the response"""
    payload = create_chat_payload(message, conversation_id)
    
    try:
        with st.spinner("🤖 Thinking..."):
            response = requests.post(CONVERSATIONAL_RPC, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to connect to AI agent: {str(e)}")
        return None

def extract_chat_response(response: Dict[str, Any]) -> str:
    """Extract the chat response from A2A response"""
    try:
        return response["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
    except (KeyError, IndexError, TypeError):
        return "I apologize, but I encountered an error processing your message."

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your AI assistant specializing in product analysis and business consulting. I can help you with:\n\n• **General questions** (time, date, business advice)\n• **Product improvement analysis** (just ask about improving any product)\n\nTry asking: *'What should I improve for iPhone 14?'* or *'What time is it?'*",
                "timestamp": datetime.now()
            }
        ]
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = "disconnected"

def check_agent_health():
    """Check if the conversational agent is running"""
    try:
        health_response = requests.get(f"http://localhost:{os.getenv('CONVERSATIONAL_AGENT_PORT', '8010')}/health", timeout=5)
        if health_response.status_code == 200:
            st.session_state.agent_status = "connected"
            return True
    except:
        pass
    
    st.session_state.agent_status = "disconnected"
    return False

def display_message(message: Dict[str, Any], is_user: bool = False):
    """Display a chat message"""
    with st.chat_message("user" if is_user else "assistant"):
        if is_user:
            st.markdown(message["content"])
        else:
            # For assistant messages, handle markdown formatting
            content = message["content"]
            
            # Check if it's a product analysis response (new human format)
            if "I've analyzed customer feedback for" in content and "My Recommendations for Your Business" in content:
                # This is our new human-formatted product analysis - display naturally
                st.markdown(content)
            # Check if it's old technical format (fallback)
            elif "📊 **Product Analysis" in content or "💼 **Business Recommendations" in content:
                # Display as expanded sections for better readability (legacy format)
                lines = content.split('\n')
                current_section = ""
                section_content = []
                
                for line in lines:
                    if line.strip().startswith('📊 **Product Analysis') or line.strip().startswith('🎯 **Overall Assessment') or line.strip().startswith('🏢 **Department Insights') or line.strip().startswith('💼 **Business Recommendations'):
                        # Start new section
                        if current_section and section_content:
                            with st.expander(current_section, expanded=True):
                                st.markdown('\n'.join(section_content))
                        current_section = line.strip()
                        section_content = []
                    elif line.strip():
                        section_content.append(line)
                
                # Display last section
                if current_section and section_content:
                    with st.expander(current_section, expanded=True):
                        st.markdown('\n'.join(section_content))
            else:
                # Regular message display
                st.markdown(content)
        
        # Show timestamp
        if "timestamp" in message:
            st.caption(f"⏰ {message['timestamp'].strftime('%H:%M')}")

def process_user_message(user_input: str):
    """Process user message and get AI response"""
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Call conversational agent
    response = call_conversational_agent(user_input, st.session_state.conversation_id)
    
    if response and "result" in response:
        # Extract and add assistant response
        ai_response = extract_chat_response(response)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.now(),
            "metadata": response.get("result", {}).get("metadata", {})
        })
        
        # Rerun to update the display
        st.rerun()
    else:
        # Error handling
        error_message = "I apologize, but I'm having trouble connecting to my analysis systems. Please try again."
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message,
            "timestamp": datetime.now()
        })
        st.rerun()

def main():
    """Main Streamlit chat application"""
    st.set_page_config(
        page_title="AI Product Analysis Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 AI Product Analysis Assistant")
    st.markdown("*Intelligent chat with advanced product analysis capabilities*")
    
    # Check agent health
    agent_online = check_agent_health()
    
    # Status indicator
    status_col1, status_col2 = st.columns([3, 1])
    with status_col2:
        if agent_online:
            st.success("🟢 Online")
        else:
            st.error("🔴 Offline")
            st.warning("⚠️ AI agent is not responding. Please ensure all services are running.")
    
    # Sidebar with conversation info
    with st.sidebar:
        st.header("💬 Conversation")
        st.write(f"**Session ID:** `{st.session_state.conversation_id[:8]}...`")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        
        # Example queries
        st.markdown("### 🎯 Try These Examples:")
        
        example_queries = [
            "What time is it?",
            "What should I improve for iPhone 14?",
            "How can I make Samsung Galaxy better?",
            "Give me recommendations for Oppo A93",
            "What's the weather like?",
            "Analyze Nike Air Max reviews"
        ]
        
        for query in example_queries:
            if st.button(f"💡 {query}", key=f"example_{hash(query)}", use_container_width=True):
                process_user_message(query)
        
        st.divider()
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
            st.rerun()
        
        # Agent capabilities
        st.markdown("### 🚀 Capabilities")
        st.markdown("""
        • **General Chat**: Ask about time, weather, or business advice
        • **Product Analysis**: Get detailed improvement recommendations
        • **Multi-Agent Analysis**: Comprehensive sentiment analysis
        • **Real-time Scraping**: Auto-fetch reviews from YouTube & Tiki
        • **Business Insights**: Actionable recommendations
        """)
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display all messages
        for message in st.session_state.messages:
            display_message(message, is_user=(message["role"] == "user"))
    
    # Chat input (fixed at bottom)
    st.divider()
    
    # Input form
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message...",
                placeholder="Ask me anything or request product analysis (e.g., 'What should I improve for iPhone 14?')",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("💬 Send", use_container_width=True)
        
        # Process input
        if send_button and user_input.strip():
            if not agent_online:
                st.error("❌ Cannot send message - AI agent is offline")
            else:
                process_user_message(user_input.strip())

if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
🤖 AI Product Analysis Assistant | Powered by Multi-Agent Architecture
</div>
""", unsafe_allow_html=True)
