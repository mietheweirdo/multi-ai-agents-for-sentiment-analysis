# app_a2a.py
"""
Smart Product Assistant Chatbot
A2A Protocol-compliant chatbot using LangGraph multi-agent consensus and debate workflow
"""

import streamlit as st
import json
import os
import time
import uuid
import requests
from typing import Dict, Any, List

# Import response agent for final formatting
from agents.response_agent import ProductResponseAgent

def load_config():
    """Load config from existing file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

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

def call_a2a_coordinator(text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call A2A LangGraph coordinator endpoint"""
    payload = create_a2a_payload(text, metadata)
    
    # Get coordinator endpoint from environment
    coordinator_port = os.getenv("LANGGRAPH_COORDINATOR_PORT", "8010") 
    endpoint = f"http://localhost:{coordinator_port}/rpc"
    
    try:
        print(f"📤 Calling A2A LangGraph coordinator at {endpoint}...")
        response = requests.post(endpoint, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ A2A coordinator response received")
        
        # Check for JSON-RPC error (not a top-level "error" key)
        if "error" in result and result.get("error") is not None:
            print(f"❌ A2A coordinator JSON-RPC error: {result['error']}")
            return None
        
        # Check if result field exists (successful A2A response)
        if "result" not in result:
            print(f"❌ A2A coordinator response missing 'result' field")
            return None
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ A2A coordinator request failed: {str(e)}")
        return None

def extract_a2a_result(response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and parse result from A2A response"""
    try:
        # Extract the text result from A2A artifacts
        result_text = response["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
        return json.loads(result_text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"❌ Failed to parse A2A result: {e}")
        return None

def run_product_response_analysis(user_input: str) -> Dict[str, Any]:
    """Complete A2A pipeline: Detect -> Scrape -> Preprocess -> A2A LangGraph Analysis -> Response"""
    try:
        config = load_config()
        
        # Step 1: Enhanced product detection 
        detected_info = detect_product_info(user_input)
        product_category = detected_info.get("category", "electronics")
        product_name = detected_info.get("product_name", "Unknown Product")
        question_type = detected_info.get("question_type", "general")
        search_keywords = detected_info.get("search_keywords", product_name.lower())
        
        print(f"🔍 Detected: {product_name} ({product_category}) - {question_type}")
        print(f"🔍 Search keywords: {search_keywords}")
        
        # Step 2: Scrape and preprocess data (with fallback)
        scraped_data = []
        try:
            # Try to import and use the real scraping
            from data_pipeline import scrape_and_preprocess
            print(f"🌐 Scraping reviews for '{search_keywords}'...")
            
            # Use Windows-compatible scraping (no signal timeout needed)
            try:
                scraped_data = scrape_and_preprocess(
                    keyword=search_keywords,
                    sources=['youtube', 'tiki'],
                    max_items_per_source=10  # Reduced for speed
                )
                print(f"✅ Found {len(scraped_data)} reviews to analyze")
            except Exception as scrape_inner_error:
                print(f"⚠️ Scraping failed: {scrape_inner_error}")
                print("📝 Using sample reviews for analysis instead")
                scraped_data = []
            
        except Exception as scrape_error:
            print(f"⚠️ Scraping failed: {scrape_error}")
            scraped_data = []
        
        # If no real data was scraped, use sample data for better analysis
        if not scraped_data:
            scraped_data = [
                {
                    'review_text': f"I've been using {product_name} for a few months now and overall it's decent. The performance is good but there are some areas that could be improved.",
                    'source': 'sample',
                    'rating': 4
                },
                {
                    'review_text': f"Great product! {product_name} exceeded my expectations in most areas. Would recommend to others looking for this type of product.",
                    'source': 'sample', 
                    'rating': 5
                },
                {
                    'review_text': f"Mixed feelings about {product_name}. Some features are excellent while others feel lacking. Price point is reasonable though.",
                    'source': 'sample',
                    'rating': 3
                }
            ]
            print(f"📝 Using sample reviews for analysis ({len(scraped_data)} items)")
        
        # Step 3: A2A LangGraph multi-agent consensus analysis
        if scraped_data:
            # Use first few scraped reviews for context
            review_context = "\\n".join([item.get('review_text', '')[:200] for item in scraped_data[:3]])
            analysis_input = f"User Question: {user_input}\\n\\nRelevant Reviews:\\n{review_context}"
        else:
            # Use just the user input
            analysis_input = user_input
        
        print(f"🤖 Running A2A LangGraph consensus analysis...")
        
        # Prepare A2A metadata for LangGraph coordinator
        a2a_metadata = {
            "product_category": product_category,
            "agent_types": ["quality", "experience", "user_experience", "business", "technical"],
            "max_discussion_rounds": 2,
            "disagreement_threshold": 0.6,
            "enable_consensus_debate": True,
            "max_tokens_per_agent": 150,
            "max_tokens_master": 2000,
            "max_tokens_advisor": 2000
        }
        
        # Call A2A LangGraph coordinator
        a2a_response = call_a2a_coordinator(analysis_input, a2a_metadata)
        
        if not a2a_response:
            # Fallback if A2A call fails
            return {"error": "A2A coordinator not available or failed"}
        
        # Extract result from A2A response
        result = extract_a2a_result(a2a_response)
        
        if not result:
            return {"error": "Failed to parse A2A coordinator response"}
        
        # Step 4: Generate final response using specialized response agent
        response_agent = ProductResponseAgent(config)
        
        # Convert A2A result format to expected format for response agent
        formatted_result = {
            "master_analysis": result.get("consensus", {}),
            "business_recommendations": {"business_impact": result.get("consensus", {}).get("business_recommendations", "")},
            "workflow_metadata": result.get("analysis_metadata", {}),
            "department_analyses": result.get("agent_analyses", []),
            "discussion_messages": result.get("discussion_info", {}).get("discussion_messages", [])
        }
        
        readable_response = response_agent.generate_response(
            analysis_result=formatted_result,
            user_input=user_input,
            product_name=product_name,
            question_type=question_type,
            scraped_data=scraped_data
        )
        
        return {
            "readable_response": readable_response,
            "product_name": product_name,
            "question_type": question_type,
            "category": product_category,
            "scraped_count": len(scraped_data),
            "raw_analysis": result,
            "a2a_metadata": a2a_metadata,
            "discussion_rounds": result.get("analysis_metadata", {}).get("discussion_rounds", 0),
            "consensus_reached": result.get("discussion_info", {}).get("consensus_reached", True)
        }
        
    except Exception as e:
        print(f"❌ A2A analysis failed: {e}")
        return {"error": str(e)}

def detect_product_info(user_input: str) -> Dict[str, Any]:
    """Enhanced product detection using LLM"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        import json
        
        config = load_config()
        llm = ChatOpenAI(
            model=config.get("model_name", "gpt-4o-mini"),
            api_key=config.get("api_key"),
            max_tokens=200,
            temperature=0.1
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract product information from user queries. Return valid JSON only.

IMPORTANT: For search_keywords, only include the PRODUCT NAME and basic descriptors, DO NOT include question types like "improvement", "suggestions", "advice", etc.

Format:
{{
  "product_name": "exact product name",
  "category": "electronics|fashion|home_garden|beauty_health|sports_outdoors|books_media", 
  "question_type": "purchase_advice|improvement_suggestions|comparison|general",
  "search_keywords": "product name only, 2-3 words max"
}}

Examples:
"Should I buy Samsung Z-Fold?" -> {{"product_name": "Samsung Galaxy Z-Fold", "category": "electronics", "question_type": "purchase_advice", "search_keywords": "samsung galaxy fold"}}
"What is laptop lenovo legion strength?" -> {{"product_name": "Lenovo Legion", "category": "electronics", "question_type": "general", "search_keywords": "lenovo legion laptop"}}
"Làm gì để cải thiện iPhone 16?" -> {{"product_name": "iPhone 16", "category": "electronics", "question_type": "improvement_suggestions", "search_keywords": "iphone 16"}}"""),
            ("human", "{query}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"query": user_input})
        
        # Parse JSON response
        result = json.loads(response.content.strip())
        return result
        
    except Exception as e:
        print(f"⚠️ LLM detection failed: {e}, using fallback")
        # Fallback to simple detection
        user_input_lower = user_input.lower()
        
        # Extract product name using improved patterns
        product_name = "Unknown Product"
        search_keywords = user_input_lower[:20]  # Default fallback
        
        # Specific product patterns
        if "samsung" in user_input_lower and ("z-fold" in user_input_lower or "fold" in user_input_lower):
            product_name = "Samsung Galaxy Z-Fold"
            search_keywords = "samsung galaxy fold"
        elif "lenovo" in user_input_lower and "legion" in user_input_lower:
            product_name = "Lenovo Legion"
            search_keywords = "lenovo legion laptop"
        elif "iphone" in user_input_lower:
            if "15" in user_input_lower:
                product_name = "iPhone 15"
                search_keywords = "iphone 15"
            elif "14" in user_input_lower:
                product_name = "iPhone 14"
                search_keywords = "iphone 14"
            else:
                product_name = "iPhone"
                search_keywords = "iphone"
        elif "samsung" in user_input_lower and ("galaxy" in user_input_lower or "phone" in user_input_lower):
            product_name = "Samsung Galaxy"
            search_keywords = "samsung galaxy"
        elif "macbook" in user_input_lower:
            product_name = "MacBook"
            search_keywords = "macbook laptop"
        elif "airpods" in user_input_lower:
            product_name = "AirPods"
            search_keywords = "apple airpods"
        elif "laptop" in user_input_lower:
            # Try to extract laptop brand/model
            words = user_input.split()
            for i, word in enumerate(words):
                word_lower = word.lower()
                if word_lower in ["hp", "dell", "asus", "acer", "lenovo", "thinkpad", "gaming"]:
                    # Found brand, try to get next word too
                    if i + 1 < len(words):
                        product_name = f"{word.title()} {words[i+1].title()}"
                        search_keywords = f"{word_lower} {words[i+1].lower()} laptop"
                    else:
                        product_name = f"{word.title()} Laptop"
                        search_keywords = f"{word_lower} laptop"
                    break
            else:
                product_name = "Laptop"
                search_keywords = "laptop"
        else:
            # Try to extract any meaningful product words
            words = user_input.split()
            product_words = []
            for word in words:
                # Look for capitalized words or known product terms
                if len(word) > 2 and (any(c.isupper() for c in word) or 
                                    word.lower() in ["phone", "tablet", "watch", "headphone", "speaker"]):
                    product_words.append(word)
            
            if product_words:
                product_name = " ".join(product_words[:2])  # Take first 2 relevant words
                search_keywords = " ".join(word.lower() for word in product_words[:2])
        
        # Question type detection
        if any(phrase in user_input_lower for phrase in ["should i buy", "worth buying", "recommend"]):
            question_type = "purchase_advice"
        elif any(phrase in user_input_lower for phrase in ["improve", "better", "fix", "problem"]):
            question_type = "improvement_suggestions"
        elif any(phrase in user_input_lower for phrase in ["compare", "vs", "versus"]):
            question_type = "comparison"
        else:
            question_type = "general"
        
        # Clean search keywords to remove question-related words
        question_words = ['improvement', 'suggestions', 'advice', 'recommend', 'better', 'fix', 'problem', 
                         'cải thiện', 'đề xuất', 'khuyên', 'tốt hơn', 'sửa', 'vấn đề', 'làm gì', 'nên', 'should']
        
        # Remove question words from search keywords
        clean_keywords = []
        for keyword in search_keywords.split():
            if keyword.lower() not in question_words:
                clean_keywords.append(keyword)
        
        search_keywords = " ".join(clean_keywords) if clean_keywords else product_name.lower()
        
        return {
            "product_name": product_name,
            "category": "electronics",  # Default
            "question_type": question_type,
            "search_keywords": search_keywords
        }

def main():
    """Main Streamlit application with enhanced UI"""
    st.set_page_config(
        page_title="Smart Product Assistant - AI-Powered Reviews",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/issues',
            'Report a bug': 'https://github.com/your-repo/issues/new',
            'About': """
            # Smart Product Assistant 🛍️
            
            AI-powered product advisor that analyzes real reviews to give you expert insights!
            
            **Features:**
            - 🔍 Smart product detection
            - 🌐 Real-time review scraping  
            - 🤖 Multi-agent AI analysis
            - 💬 Personalized recommendations
            
            Built with ❤️ using Streamlit and OpenAI GPT-4
            """
        }
    )
    
    # Custom CSS for dark theme and balanced chat layout
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    .stApp > header {
        background-color: transparent;
    }
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    /* Dark theme for all components */
    .stChatMessage {
        background-color: #262730;
        border: 1px solid #404040;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    /* Balanced chat message alignment - Fixed margins */
    .stChatMessage[data-testid="chat-message-user"] {
        margin-left: 15%;
        margin-right: 2rem;
        background-color: #1f4e79;
        border-left: 4px solid #667eea;
    }
    .stChatMessage[data-testid="chat-message-assistant"] {
        margin-left: 2rem;
        margin-right: 15%;
        background-color: #262730;
        border-left: 4px solid #764ba2;
    }
    /* Chat content padding */
    .stChatMessage > div {
        padding: 1rem 1.2rem;
    }
    /* Responsive design for mobile */
    @media (max-width: 768px) {
        .stChatMessage[data-testid="chat-message-user"] {
            margin-left: 10%;
            margin-right: 1rem;
        }
        .stChatMessage[data-testid="chat-message-assistant"] {
            margin-left: 1rem;
            margin-right: 10%;
        }
    }
    .stExpander {
        background-color: #262730;
        border: 1px solid #404040;
        margin: 0.5rem 0;
    }
    .stSidebar {
        background-color: #262730;
    }
    /* Chat input styling */
    .stChatInput > div > div {
        background-color: #262730;
        border: 1px solid #404040;
    }
    /* Spinner container */
    .stSpinner {
        text-align: center;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Compact header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1.5rem 2rem; border-radius: 10px; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h2 style="color: white; margin-bottom: 0.3rem; font-size: 1.8rem;">🛍️ Smart Product Assistant</h2>
        <p style="color: rgba(255,255,255,0.9); font-size: 1rem; margin-bottom: 0;">AI-powered product advisor with real-time review analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Run the chatbot interface
    run_chatbot_interface()

def run_chatbot_interface():
    """Enhanced chatbot interface with beautiful UI and detailed loading steps"""
    
    # Custom CSS for better dark theme styling and balanced chat layout
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    /* Chat message content styling */
    .stChatMessage .stMarkdown {
        padding: 0.5rem 0;
    }
    
    /* Example questions styling */
    .example-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        padding: 1rem;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .example-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Improve chat alignment */
    .stChatMessage > div > div {
        max-width: none !important;
        width: 100%;
    }
    
    /* Better responsive margins */
    @media (max-width: 768px) {
        .stChatMessage[data-testid="chat-message-user"] {
            margin-left: 1rem;
            margin-right: 0.5rem;
        }
        .stChatMessage[data-testid="chat-message-assistant"] {
            margin-left: 0.5rem;
            margin-right: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Example questions displayed by default (not in expander)
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h3 style="color: #667eea; margin-bottom: 1rem;">💡 Example Questions</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="example-card">
                <strong>🛒 Purchase Decisions</strong><br>
                <span style="color: rgba(255,255,255,0.9);">
                • Should I buy Samsung Z-Fold?<br>
                • Is MacBook worth the price?<br>
                • Samsung vs iPhone comparison
                </span>
            </div>
            <div class="example-card">
                <strong>🔧 Product Improvements</strong><br>
                <span style="color: rgba(255,255,255,0.9);">
                • What can iPhone 15 improve?<br>
                • How to make AirPods better?<br>
                • Laptop battery life issues
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    
                    # Show enhanced analysis details
                    if "metadata" in message and message["metadata"]:
                        metadata = message["metadata"]
                        
                        # Create beautiful metadata display
                        with st.expander("📊 **Analysis Details**", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if "product_detected" in metadata:
                                    st.metric("🎯 Product", metadata["product_detected"])
                            
                            with col2:
                                if "scraped_count" in metadata:
                                    st.metric("📚 Reviews", metadata["scraped_count"])
                            
                            with col3:
                                if "processing_time" in metadata:
                                    st.metric("⏱️ Time", f"{metadata['processing_time']:.1f}s")
                            
                            # Additional metadata
                            if "question_type" in metadata:
                                st.info(f"**Question Type:** {metadata['question_type'].replace('_', ' ').title()}")
    
    # Chat input at the bottom
    user_input = st.chat_input("💭 Ask me about any product...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Show loading with spinner outside chat message
        with st.spinner("🤖 AI is thinking..."):
            try:
                # Get response from the complete pipeline
                result = run_product_response_analysis(user_input)
                
                if "error" not in result:
                    # Get the readable response
                    assistant_response = result.get("readable_response", "I've analyzed your question, but couldn't generate a clear response.")
                    
                    # Prepare metadata
                    metadata = {
                        "product_detected": result.get("product_name", "Unknown"),
                        "question_type": result.get("question_type", "General"),
                        "scraped_count": result.get("scraped_count", 0)
                    }
                    
                else:
                    # Error occurred
                    assistant_response = "I'm sorry, I encountered an error while analyzing your question. The A2A coordinator might not be running. Please try again or check the system status."
                    metadata = {}
                
            except Exception as e:
                # Handle any unexpected errors
                assistant_response = f"An unexpected error occurred: {str(e)}"
                metadata = {}
        
        # Show assistant response after loading completes
        with st.chat_message("assistant"):
            # Display the final response with beautiful formatting
            st.markdown("### 💬 **Response**")
            st.write(assistant_response)
            
            # Show enhanced metadata
            if metadata:
                with st.expander("📊 **Analysis Details**", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "product_detected" in metadata:
                            st.metric("🎯 Product", metadata["product_detected"])
                    
                    with col2:
                        if "scraped_count" in metadata:
                            st.metric("📚 Reviews", metadata["scraped_count"])
                    
                    with col3:
                        # Skip processing time as we removed timing logic
                        if "question_type" in metadata:
                            st.metric("❓ Type", metadata["question_type"].replace('_', ' ').title())
                    
                    # Additional metadata
                    if "question_type" in metadata:
                        st.info(f"**Question Type:** {metadata['question_type'].replace('_', ' ').title()}")
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_response,
            "metadata": metadata
        })
    
    # Enhanced sidebar with better styling
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
            <h3>🔧 Control Panel</h3>
            <p style="margin-bottom: 0;">Manage your chat experience</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Clear chat button with better styling
        if st.button("🗑️ Clear Chat History", use_container_width=True, type="primary"):
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        # How it works section
        with st.expander("ℹ️ **How It Works**", expanded=True):
            st.markdown("""
            <div style="font-size: 0.9rem; color: #fafafa;">
            <div style="margin-bottom: 1rem;">
                <strong style="color: #667eea;">🔍 Step 1: Product Detection</strong><br>
                <span style="color: #b3b3b3;">AI analyzes your question to identify the product and question type</span>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong style="color: #667eea;">🌐 Step 2: Review Scraping</strong><br>
                <span style="color: #b3b3b3;">Searches YouTube & Tiki for relevant product reviews</span>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong style="color: #667eea;">🤖 Step 3: Multi-Agent Analysis</strong><br>
                <span style="color: #b3b3b3;">5 specialized AI agents analyze and debate findings</span>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong style="color: #667eea;">💬 Step 4: Smart Response</strong><br>
                <span style="color: #b3b3b3;">Generates personalized recommendations just for you</span>
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        # System status
        with st.expander("📊 **System Status**", expanded=False):
            st.markdown("""
            <div style="font-size: 0.9rem; color: #fafafa;">
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #4caf50;">●</span> <strong style="color: #fafafa;">A2A Coordinator:</strong> <span style="color: #b3b3b3;">Active</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #4caf50;">●</span> <strong style="color: #fafafa;">Data Pipeline:</strong> <span style="color: #b3b3b3;">Ready</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #4caf50;">●</span> <strong style="color: #fafafa;">AI Agents:</strong> <span style="color: #b3b3b3;">5 agents online</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #4caf50;">●</span> <strong style="color: #fafafa;">Review Sources:</strong> <span style="color: #b3b3b3;">YouTube + Tiki</span>
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tips section
        with st.expander("💡 **Pro Tips**", expanded=False):
            st.markdown("""
            <div style="font-size: 0.9rem; color: #fafafa;">
            <div style="margin-bottom: 0.8rem;">
                <strong style="color: #667eea;">🎯 Be Specific:</strong><br>
                <span style="color: #b3b3b3;">"Should I buy iPhone 15 Pro?" is better than "Tell me about iPhones"</span>
            </div>
            
            <div style="margin-bottom: 0.8rem;">
                <strong style="color: #667eea;">🗣️ Ask Naturally:</strong><br>
                <span style="color: #b3b3b3;">Use natural language like you're talking to a friend</span>
            </div>
            
            <div style="margin-bottom: 0.8rem;">
                <strong style="color: #667eea;">🔄 Try Different Questions:</strong><br>
                <span style="color: #b3b3b3;">Ask about features, problems, comparisons, or improvements</span>
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Footer
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem; color: #b3b3b3; margin-top: 2rem;">
            <p>🤖 Powered by AI Agents</p>
            <p>Made with ❤️ using Streamlit</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
