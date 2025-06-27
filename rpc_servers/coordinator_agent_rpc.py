# rpc_servers/coordinator_agent_rpc.py
"""
Coordinator Agent RPC Server - A2A compatible JSON-RPC endpoint
Orchestrates multi-agent sentiment analysis using your existing EnhancedCoordinatorAgent
"""

import os
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for module imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing agent functionality
from agents.enhanced_coordinator import EnhancedCoordinatorAgent

import os
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for module imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing agent functionality
from agents.enhanced_coordinator import EnhancedCoordinatorAgent

# Load environment variables
load_dotenv()

# Import existing coordinator functionality  
from agents.enhanced_coordinator import EnhancedCoordinatorAgent
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
    title="Multi-Agent Sentiment Coordinator RPC Server",
    description="A2A-compatible coordinator for multi-agent sentiment analysis",
    version="0.1.0"
)

# Setup agent card endpoint
setup_agent_card_endpoint(
    app, 
    os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards", "coordinator_agent_card.json")
)

# Load configuration
config = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model_name": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
}

# Global coordinator instance (can be reconfigured per request)
coordinator = None

def create_coordinator(
    product_category: str = "electronics",
    agent_types: Optional[List[str]] = None,
    max_tokens_per_agent: int = 150,
    max_tokens_consensus: int = 800,
    max_rounds: int = 2
) -> EnhancedCoordinatorAgent:
    """Create a coordinator with specified configuration"""
    
    if agent_types is None:
        agent_types = ["quality", "experience", "user_experience", "business"]
    
    return EnhancedCoordinatorAgent(
        config=config,
        product_category=product_category,
        agent_types=agent_types,
        max_tokens_per_agent=max_tokens_per_agent,
        max_rounds=max_rounds,
        max_tokens_consensus=max_tokens_consensus
    )

@app.post("/rpc", response_model=JsonRpcResponse)
async def rpc_handler(rpc_req: JsonRpcRequest) -> JsonRpcResponse:
    """
    Handle JSON-RPC 2.0 requests for coordinated multi-agent sentiment analysis.
    
    Expected payload:
    {
        "jsonrpc": "2.0",
        "id": "<uuid>",
        "method": "tasks/send",
        "params": {
            "id": "<uuid>",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": "<review_text>"}]
            },
            "metadata": {
                "product_category": "electronics",  # optional
                "agent_types": ["quality", "experience", "user_experience", "business"],  # optional
                "max_tokens_per_agent": 150,  # optional
                "max_tokens_consensus": 800,  # optional
                "max_rounds": 2  # optional
            }
        }
    }
    """
    global coordinator
    
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
        agent_types = metadata.get("agent_types", ["quality", "experience", "user_experience", "business"])
        max_tokens_per_agent = metadata.get("max_tokens_per_agent", int(os.getenv("DEFAULT_MAX_TOKENS_PER_AGENT", "150")))
        max_tokens_consensus = metadata.get("max_tokens_consensus", int(os.getenv("DEFAULT_MAX_TOKENS_CONSENSUS", "800")))
        max_rounds = metadata.get("max_rounds", int(os.getenv("DEFAULT_MAX_ROUNDS", "2")))
        
        logger.info(f"Coordinating sentiment analysis for category: {product_category}")
        logger.info(f"Agent types: {agent_types}")
        logger.info(f"Review text: {review_text[:100]}...")
        
        # Create or reconfigure coordinator if needed
        if (coordinator is None or 
            coordinator.product_category != product_category or
            len(coordinator.sentiment_agents) != len(agent_types) or
            coordinator.max_tokens_per_agent != max_tokens_per_agent):
            
            logger.info("Creating new coordinator with specified configuration")
            coordinator = create_coordinator(
                product_category=product_category,
                agent_types=agent_types,
                max_tokens_per_agent=max_tokens_per_agent,
                max_tokens_consensus=max_tokens_consensus,
                max_rounds=max_rounds
            )
        
        # Run coordinated analysis using your existing workflow
        analysis_result = coordinator.run_workflow(
            reviews=[review_text],  # EnhancedCoordinatorAgent expects a list
            product_category=product_category
        )
        
        # Format result as JSON string for A2A response
        import json
        output_text = json.dumps(analysis_result, indent=2)
        
        # Extract key metrics for metadata
        consensus = analysis_result.get('consensus', {})
        overall_sentiment = consensus.get('overall_sentiment', 'unknown')
        overall_confidence = consensus.get('overall_confidence', 0.0)
        
        logger.info(f"Coordinated analysis completed. Overall sentiment: {overall_sentiment}")
        logger.info(f"Overall confidence: {overall_confidence:.2f}")
        
        # Create A2A-compliant response
        return create_a2a_response(
            request_id=rpc_req.id,
            task_id=rpc_req.params.get("id"),
            output_text=output_text,
            session_id=f"coordinator-session-{rpc_req.params.get('id', 'unknown')[:8]}",
            metadata={
                "agent_type": "coordinator",
                "product_category": product_category,
                "agent_types": agent_types,
                "max_tokens_per_agent": max_tokens_per_agent,
                "max_tokens_consensus": max_tokens_consensus,
                "overall_sentiment": overall_sentiment,
                "overall_confidence": overall_confidence,
                "total_agents": len(agent_types),
                "discussion_rounds": analysis_result.get('analysis_metadata', {}).get('discussion_rounds', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Coordinator analysis failed: {str(e)}")
        return create_error_response(
            rpc_req.id,
            -32603,
            f"Coordinator analysis failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "agent": "coordinator", 
        "version": "0.1.0",
        "available_categories": ["electronics", "fashion", "home_garden", "beauty_health", "sports_outdoors", "books_media"],
        "available_agent_types": ["quality", "experience", "user_experience", "business", "technical"]
    }

@app.get("/config")
async def get_config():
    """Get current coordinator configuration"""
    global coordinator
    if coordinator is None:
        return {"status": "not_initialized"}
    
    return {
        "product_category": coordinator.product_category,
        "agent_types": [agent.agent_type for agent in coordinator.sentiment_agents],
        "max_tokens_per_agent": coordinator.max_tokens_per_agent,
        "max_tokens_consensus": coordinator.max_tokens_consensus,
        "max_rounds": coordinator.max_rounds,
        "total_agents": len(coordinator.sentiment_agents)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("COORDINATOR_AGENT_PORT", "8000"))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    reload = os.getenv("FASTAPI_RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting Multi-Agent Sentiment Coordinator RPC Server on {host}:{port}")
    uvicorn.run(
        "coordinator_agent_rpc:app",
        host=host,
        port=port,
        reload=reload
    )
