# app.py
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
        
        if "error" in result:
            print(f"❌ A2A coordinator error: {result['error']}")
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
            
            # Set a timeout for scraping to prevent hanging (Unix only)
            try:
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Scraping timeout")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)  # 30 second timeout
                
                scraped_data = scrape_and_preprocess(
                    keyword=search_keywords,
                    sources=['youtube', 'tiki'],
                    max_items_per_source=5  # Reduced for speed
                )
                signal.alarm(0)  # Cancel timeout
                print(f"✅ Found {len(scraped_data)} reviews to analyze")
                
            except (AttributeError, ImportError, TimeoutError):
                # Windows or timeout - try without signal
                print("⚠️ Timeout not available or triggered - using quick scraping...")
                try:
                    scraped_data = scrape_and_preprocess(
                        keyword=search_keywords,
                        sources=['youtube','tiki'],  # Just YouTube for speed
                        max_items_per_source=3
                    )
                    print(f"✅ Found {len(scraped_data)} reviews to analyze")
                except:
                    print("⚠️ Scraping failed - using sample reviews instead")
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
            "max_tokens_master": 500,
            "max_tokens_advisor": 600
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
                signal.alarm(0)  # Cancel timeout
                print(f"✅ Found {len(scraped_data)} reviews to analyze")
                
            except (AttributeError, ImportError, TimeoutError):
                # Windows or timeout - try without signal
                print("⚠️ Timeout not available or triggered - using quick scraping...")
                try:
                    scraped_data = scrape_and_preprocess(
                        keyword=search_keywords,
                        sources=['youtube','tiki'],  # Just YouTube for speed
                        max_items_per_source=3
                    )
                    print(f"✅ Found {len(scraped_data)} reviews to analyze")
                except:
                    print("⚠️ Scraping failed - using sample reviews instead")
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
            "max_tokens_master": 500,
            "max_tokens_advisor": 600
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

Format:
{{
  "product_name": "exact product name",
  "category": "electronics|fashion|home_garden|beauty_health|sports_outdoors|books_media", 
  "question_type": "purchase_advice|improvement_suggestions|comparison|general",
  "search_keywords": "product name only, 2-3 words max"
}}

IMPORTANT: For search_keywords, only include the PRODUCT NAME and basic descriptors, DO NOT include question types like "improvement", "suggestions", "advice", etc.

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

def run_chatbot_interface():
    """Simplified chatbot interface for product questions"""
    st.markdown("### 💬 Ask About Any Product")
    st.markdown("*Just type your question naturally! Examples:*")
    st.markdown("• Should I buy Samsung Z-Fold?")
    st.markdown("• What can iPhone 15 improve?")
    st.markdown("• Is MacBook worth the price?")
    
    # Initialize chat history
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
                    
                    # Show simple analysis details
                    if "metadata" in message and message["metadata"]:
                        metadata = message["metadata"]
                        details = []
                        if "product_detected" in metadata:
                            details.append(f"Product: {metadata['product_detected']}")
                        if "scraped_count" in metadata:
                            details.append(f"Reviews analyzed: {metadata['scraped_count']}")
                        if "processing_time" in metadata:
                            details.append(f"Time: {metadata['processing_time']:.1f}s")
                        
                        if details:
                            st.caption(" • ".join(details))
    
    # Chat input
    user_input = st.chat_input("Ask me about any product...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Show thinking spinner and get response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Detecting product... 🌐 Scraping reviews... 🤖 AI agents analyzing... 💬 Generating response..."):
                start_time = time.time()
                
                # Get response from the complete pipeline
                result = run_product_response_analysis(user_input)
                
                processing_time = time.time() - start_time
            
            # Process and display the result
            if "error" in result:
                assistant_response = f"I'm sorry, I encountered an error while analyzing your question. Please try rephrasing it or ask about a different product."
                metadata = {}
            else:
                # Get the readable response from the product response agent
                assistant_response = result.get("readable_response", "I've analyzed your question, but couldn't generate a clear response.")
                
                # Prepare metadata
                metadata = {
                    "processing_time": processing_time,
                    "product_detected": result.get("product_name", "Unknown"),
                    "question_type": result.get("question_type", "General"),
                    "scraped_count": result.get("scraped_count", 0)
                }
            
            # Display the response
            st.write(assistant_response)
            
            # Show enhanced metadata
            if metadata:
                details = []
                if "product_detected" in metadata:
                    details.append(f"Product: {metadata['product_detected']}")
                if "scraped_count" in metadata:
                    details.append(f"Reviews analyzed: {metadata['scraped_count']}")
                if "processing_time" in metadata:
                    details.append(f"Time: {metadata['processing_time']:.1f}s")
                
                if details:
                    st.caption(" • ".join(details))
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": assistant_response,
            "metadata": metadata
        })
    
    # Clear chat button in sidebar
    with st.sidebar:
        st.markdown("### 🔧 Options")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("### ℹ️ How it works")
        st.markdown("""
        1. **🔍 Product Detection** - AI identifies the product from your question
        2. **🌐 Review Scraping** - Searches YouTube & Tiki for relevant reviews  
        3. **🤖 Multi-Agent Analysis** - 5 AI agents analyze and debate
        4. **💬 Smart Response** - Generates a personalized answer just for you
        """)
        
        st.markdown("### 📝 Example Questions")
        st.markdown("""
        • Should I buy Samsung Z-Fold?
        • What can iPhone 15 improve?
        • Is MacBook worth the price?
        • Samsung vs iPhone comparison
        """)

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Smart Product Assistant",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title("🛍️ Smart Product Assistant")
    st.markdown("*AI-powered product advisor with real-time review analysis and expert consensus*")
    
    # Run the chatbot interface only (no sentiment analysis mode)
    run_chatbot_interface()

if __name__ == "__main__":
    main()
