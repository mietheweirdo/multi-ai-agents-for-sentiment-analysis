"""
Conversational Agent RPC Server - A2A compatible JSON-RPC endpoint
Handles intelligent chat with product analysis integration
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for module imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import conversational agent functionality
from agents.conversational_agent import ConversationalAgent
from shared.json_rpc.base import (
    JsonRpcRequest, 
    JsonRpcResponse,
    create_a2a_response,
    create_error_response,
    extract_text_from_message,
    setup_agent_card_endpoint,
    validate_rpc_request
)

# Setup logging
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Conversational Agent RPC Server",
    description="A2A-compatible intelligent chat agent with product analysis",
    version="0.1.0"
)

# Setup agent card endpoint
setup_agent_card_endpoint(
    app, 
    os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards", "conversational_agent_card.json")
)

# Load configuration
config = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model_name": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
}

# Initialize the conversational agent
use_a2a = os.getenv("USE_A2A_COORDINATOR", "false").lower() == "true"
if use_a2a:
    coordinator_endpoint = f"http://localhost:{os.getenv('A2A_COORDINATOR_PORT', '8020')}/rpc"
    logger.info("🔗 Using Enhanced A2A Coordinator for true agent-to-agent communication")
else:
    coordinator_endpoint = f"http://localhost:{os.getenv('COORDINATOR_AGENT_PORT', '8000')}/rpc"
    logger.info("🔗 Using Standard Coordinator")

conversational_agent = ConversationalAgent(
    config=config, 
    coordinator_endpoint=coordinator_endpoint,
    use_a2a_coordinator=use_a2a
)

@app.post("/rpc", response_model=JsonRpcResponse)
async def rpc_handler(rpc_req: JsonRpcRequest) -> JsonRpcResponse:
    """
    Handle JSON-RPC 2.0 requests for conversational chat.
    
    Expected payload:
    {
        "jsonrpc": "2.0",
        "id": "<uuid>",
        "method": "tasks/send",
        "params": {
            "id": "<uuid>",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": "<user_message>"}]
            },
            "metadata": {
                "conversation_id": "optional_conversation_id",
                "user_id": "optional_user_id"
            }
        }
    }
    """
    logger.info(f"Received RPC request: {rpc_req.method}")
    
    # Validate request
    error_response = validate_rpc_request(rpc_req)
    if error_response:
        return error_response
    
    try:
        # Extract input text
        message = rpc_req.params["message"]
        user_message = extract_text_from_message(message)
        
        # Get optional parameters from metadata
        metadata = rpc_req.params.get("metadata", {})
        conversation_id = metadata.get("conversation_id", "default")
        user_id = metadata.get("user_id", "anonymous")
        
        logger.info(f"Processing message from user {user_id}: {user_message[:100]}...")
        
        # Process the message through conversational agent
        response_data = conversational_agent.process_message(user_message)
        
        # Format response based on type
        if response_data.get('type') == 'product_analysis':
            # Product analysis response
            if response_data.get('success'):
                analysis = response_data.get('analysis', {})
                product_name = response_data.get('product_name', 'Unknown')
                
                # Use human-formatted response if available, otherwise fall back to technical format
                if 'human_response' in response_data:
                    output_text = response_data['human_response']
                else:
                    # Fallback to technical format
                    output_text = format_product_analysis_response(analysis, product_name)
                
                # Add analysis metadata
                response_metadata = {
                    "agent_type": "conversational",
                    "response_type": "product_analysis",
                    "product_name": product_name,
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "analysis_summary": {
                        "overall_sentiment": analysis.get('master_analysis', {}).get('sentiment', 'unknown'),
                        "confidence": analysis.get('master_analysis', {}).get('confidence', 0.0),
                        "departments_analyzed": len(analysis.get('department_analyses', [])),
                        "has_business_recommendations": bool(analysis.get('business_recommendations'))
                    }
                }
            else:
                # Analysis failed
                error_msg = response_data.get('error', 'Analysis failed')
                output_text = f"I apologize, but I couldn't analyze the product: {error_msg}. Please try again or ask about a different product."
                response_metadata = {
                    "agent_type": "conversational",
                    "response_type": "error",
                    "error": error_msg,
                    "conversation_id": conversation_id,
                    "user_id": user_id
                }
        
        else:
            # General chat response
            output_text = response_data.get('response', 'I apologize, but I could not process your message.')
            response_metadata = {
                "agent_type": "conversational",
                "response_type": response_data.get('type', 'general_chat'),
                "conversation_id": conversation_id,
                "user_id": user_id
            }
            
            # Add suggestions if available
            if 'suggestions' in response_data:
                response_metadata['suggestions'] = response_data['suggestions']
        
        logger.info(f"Conversational response generated: {response_data.get('type', 'unknown')} type")
        
        # Create A2A-compliant response
        return create_a2a_response(
            request_id=rpc_req.id,
            task_id=rpc_req.params.get("id"),
            output_text=output_text,
            session_id=f"conv-session-{conversation_id}-{rpc_req.params.get('id', 'unknown')[:8]}",
            metadata=response_metadata
        )
        
    except Exception as e:
        logger.error(f"Conversational agent processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_error_response(
            rpc_req.id,
            -32603,
            f"Conversational agent processing failed: {str(e)}"
        )

def format_product_analysis_response(analysis: dict, product_name: str) -> str:
    """Format product analysis results for chat display"""
    try:
        response_parts = []
        
        # Header
        response_parts.append(f"📊 **Product Analysis for {product_name}**")
        response_parts.append("")
        
        # Master analysis summary
        master_analysis = analysis.get('master_analysis', {})
        if master_analysis:
            sentiment = master_analysis.get('sentiment', 'unknown').title()
            confidence = master_analysis.get('confidence', 0.0)
            reasoning = master_analysis.get('reasoning', 'No reasoning provided')
            
            response_parts.append(f"🎯 **Overall Assessment**: {sentiment} ({confidence:.1%} confidence)")
            response_parts.append(f"📝 **Reasoning**: {reasoning}")
            response_parts.append("")
        
        # Department insights
        departments = analysis.get('department_analyses', [])
        if departments:
            response_parts.append("🏢 **Department Insights**:")
            for dept in departments:
                agent_type = dept.get('agent_type', 'unknown').replace('_', ' ').title()
                sentiment = dept.get('sentiment', 'unknown').title()
                confidence = dept.get('confidence', 0.0)
                
                response_parts.append(f"• **{agent_type}**: {sentiment} ({confidence:.1%})")
            response_parts.append("")
        
        # Business recommendations (most important)
        business_rec = analysis.get('business_recommendations', {})
        if business_rec:
            response_parts.append("💼 **Business Recommendations**:")
            
            business_impact = business_rec.get('business_impact', '')
            if business_impact:
                response_parts.append(business_impact)
            
            reasoning = business_rec.get('reasoning', '')
            if reasoning:
                response_parts.append("")
                response_parts.append(f"**Reasoning**: {reasoning}")
            
            # Add emotions and topics if available
            emotions = business_rec.get('emotions', [])
            topics = business_rec.get('topics', [])
            
            if emotions or topics:
                response_parts.append("")
                if emotions:
                    response_parts.append(f"😊 **Key Customer Emotions**: {', '.join(emotions)}")
                if topics:
                    response_parts.append(f"📌 **Focus Areas**: {', '.join(topics)}")
        
        # Metadata
        metadata = analysis.get('workflow_metadata', {})
        if metadata:
            processing_time = metadata.get('processing_time', 0)
            discussion_rounds = metadata.get('discussion_rounds', 0)
            
            response_parts.append("")
            response_parts.append(f"⚙️ **Analysis Details**: {processing_time:.1f}s processing, {discussion_rounds} discussion rounds")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Failed to format analysis response: {e}")
        return f"Analysis completed for {product_name}, but I encountered an error formatting the results. Please try again."

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    use_a2a = os.getenv("USE_A2A_COORDINATOR", "false").lower() == "true"
    
    return {
        "status": "healthy", 
        "agent": "conversational", 
        "version": "0.1.0",
        "capabilities": [
            "general_chat",
            "product_analysis",
            "intent_detection",
            "a2a_integration",
            "human_advisor_responses"
        ],
        "coordinator_endpoint": conversational_agent.coordinator_endpoint,
        "coordinator_type": conversational_agent.coordinator_type,
        "metadata": {
            "using_a2a_coordinator": use_a2a,
            "communication_protocol": "A2A JSON-RPC" if use_a2a else "Standard RPC",
            "response_format": "human_advisor"
        }
    }

@app.get("/config")
async def get_config():
    """Get agent configuration"""
    return {
        "agent_type": "conversational",
        "coordinator_endpoint": coordinator_endpoint,
        "supported_intents": ["general_chat", "product_analysis", "clarification_needed"],
        "product_keywords": conversational_agent.product_keywords[:10],  # Show first 10
        "capabilities": [
            "Intelligent intent detection",
            "General conversation handling",
            "Product improvement analysis",
            "Multi-agent coordination",
            "Business recommendations"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CONVERSATIONAL_AGENT_PORT", "8010"))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    reload = os.getenv("FASTAPI_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting Conversational Agent RPC Server on {host}:{port}")
    uvicorn.run(
        "conversational_agent_rpc:app",
        host=host,
        port=port,
        reload=reload
    ) 