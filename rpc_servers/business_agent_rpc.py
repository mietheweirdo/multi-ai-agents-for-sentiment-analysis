# rpc_servers/business_agent_rpc.py
"""
Business Impact Agent RPC Server - A2A compatible JSON-RPC endpoint
Handles market impact and business implications sentiment analysis
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
from agents.sentiment_agents import BusinessImpactAgent
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
    title="Business Impact Agent RPC Server",
    description="A2A-compatible sentiment analysis agent focusing on market impact and business implications",
    version="0.1.0"
)

# Setup agent card endpoint
setup_agent_card_endpoint(
    app, 
    os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards", "business_agent_card.json")
)

# Load configuration
config = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model_name": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
}

# Initialize the business agent (will be created per request to allow product category customization)
def create_business_agent(product_category: str = "electronics", max_tokens: int = 150) -> BusinessImpactAgent:
    """Create a business impact agent with specified configuration"""
    return BusinessImpactAgent(
        config=config,
        max_tokens=max_tokens,
        product_category=product_category
    )

@app.post("/rpc", response_model=JsonRpcResponse)
async def rpc_handler(rpc_req: JsonRpcRequest) -> JsonRpcResponse:
    """Handle JSON-RPC 2.0 requests for business impact sentiment analysis"""
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
        
        logger.info(f"Analyzing business impact sentiment for category: {product_category}")
        logger.info(f"Review text: {review_text[:100]}...")
        
        # Create and run business agent analysis
        business_agent = create_business_agent(product_category, max_tokens)
        analysis_result = business_agent.analyze(review_text)
        
        # Format result as JSON string for A2A response
        import json
        output_text = json.dumps(analysis_result, indent=2)
        
        logger.info(f"Business analysis completed. Sentiment: {analysis_result.get('sentiment', 'unknown')}")
        
        # Create A2A-compliant response
        return create_a2a_response(
            request_id=rpc_req.id,
            task_id=rpc_req.params.get("id"),
            output_text=output_text,
            session_id=f"business-session-{rpc_req.params.get('id', 'unknown')[:8]}",
            metadata={
                "agent_type": "business",
                "product_category": product_category,
                "max_tokens": max_tokens,
                "sentiment": analysis_result.get('sentiment'),
                "confidence": analysis_result.get('confidence')
            }
        )
        
    except Exception as e:
        logger.error(f"Business agent analysis failed: {str(e)}")
        return create_error_response(
            rpc_req.id,
            -32603,
            f"Business agent analysis failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "business", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BUSINESS_AGENT_PORT", "8004"))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    reload = os.getenv("FASTAPI_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting Business Impact Agent RPC Server on {host}:{port}")
    uvicorn.run(
        "business_agent_rpc:app",
        host=host,
        port=port,
        reload=reload
    )
