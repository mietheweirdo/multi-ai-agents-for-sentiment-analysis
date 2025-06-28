# rpc_servers/technical_agent_rpc.py
"""
Technical Specification Agent RPC Server - A2A compatible JSON-RPC endpoint
Handles technical specifications and features sentiment analysis
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

# Import existing agent functionality
from agents.sentiment_agents import TechnicalSpecAgent
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
    title="Technical Specification Agent RPC Server",
    description="A2A-compatible sentiment analysis agent focusing on technical specifications and features",
    version="0.1.0"
)

# Setup agent card endpoint
setup_agent_card_endpoint(
    app, 
    os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards", "technical_agent_card.json")
)

# Load configuration
config = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model_name": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
}

# Initialize the technical agent (will be created per request to allow product category customization)
def create_technical_agent(product_category: str = "electronics", max_tokens: int = 150) -> TechnicalSpecAgent:
    """Create a technical specification agent with specified configuration"""
    return TechnicalSpecAgent(
        config=config,
        max_tokens=max_tokens,
        product_category=product_category
    )

@app.post("/rpc", response_model=JsonRpcResponse)
async def rpc_handler(rpc_req: JsonRpcRequest) -> JsonRpcResponse:
    """Handle JSON-RPC 2.0 requests for technical specification sentiment analysis"""
    logger.info(f"Received RPC request: {rpc_req.method}")
    
    # Validate request
    error_response = validate_rpc_request(rpc_req)
    if error_response:
        return error_response
    
    try:
        # Extract input text
        message = rpc_req.params["message"]
        review_text = extract_text_from_message(message)
        
        # Get optional parameters from metadata
        metadata = rpc_req.params.get("metadata", {})
        product_category = metadata.get("product_category", os.getenv("DEFAULT_PRODUCT_CATEGORY", "electronics"))
        max_tokens = metadata.get("max_tokens", int(os.getenv("DEFAULT_MAX_TOKENS_PER_AGENT", "150")))
        
        logger.info(f"Analyzing technical sentiment for category: {product_category}")
        logger.info(f"Review text: {review_text[:100]}...")
        
        # Create and run technical agent analysis
        technical_agent = create_technical_agent(product_category, max_tokens)
        analysis_result = technical_agent.analyze(review_text)
        
        # Format result as JSON string for A2A response
        import json
        output_text = json.dumps(analysis_result, indent=2)
        
        logger.info(f"Technical analysis completed. Sentiment: {analysis_result.get('sentiment', 'unknown')}")
        
        # Create A2A-compliant response
        return create_a2a_response(
            request_id=rpc_req.id,
            task_id=rpc_req.params.get("id"),
            output_text=output_text,
            session_id=f"technical-session-{rpc_req.params.get('id', 'unknown')[:8]}",
            metadata={
                "agent_type": "technical",
                "product_category": product_category,
                "max_tokens": max_tokens,
                "sentiment": analysis_result.get('sentiment'),
                "confidence": analysis_result.get('confidence')
            }
        )
        
    except Exception as e:
        logger.error(f"Technical agent analysis failed: {str(e)}")
        return create_error_response(
            rpc_req.id,
            -32603,
            f"Technical agent analysis failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "technical", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("TECHNICAL_AGENT_PORT", "8005"))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    reload = os.getenv("FASTAPI_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting Technical Specification Agent RPC Server on {host}:{port}")
    uvicorn.run(
        "technical_agent_rpc:app",
        host=host,
        port=port,
        reload=reload
    )
