# rpc_servers/langgraph_coordinator_rpc.py
"""
LangGraph A2A Coordinator RPC Server - A2A compatible JSON-RPC endpoint
Orchestrates multi-agent sentiment analysis using LangGraph consensus and debate workflow
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for module imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import LangGraph coordinator functionality
from agents.langgraph_coordinator import LangGraphCoordinator, analyze_with_langgraph
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
    title="LangGraph Multi-Agent Sentiment Coordinator RPC Server",
    description="A2A-compatible LangGraph coordinator with consensus and debate workflow",
    version="1.0.0"
)

# Setup agent card endpoint
setup_agent_card_endpoint(
    app, 
    os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards", "langgraph_coordinator_card.json")
)

# Load configuration
def load_config():
    """Load config from existing file"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config.json: {e}, using environment variables")
        return {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model_name": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        }

config = load_config()

# Global coordinator instance (can be reconfigured per request)
coordinator_cache = {}

def create_langgraph_coordinator(
    product_category: str = "electronics",
    agent_types: Optional[List[str]] = None,
    max_tokens_per_agent: int = 150,
    max_tokens_master: int = 500,
    max_tokens_advisor: int = 600,
    max_discussion_rounds: int = 2,
    disagreement_threshold: float = 0.6
) -> LangGraphCoordinator:
    """Create a LangGraph coordinator with specified configuration"""
    
    if agent_types is None:
        agent_types = ["quality", "experience", "user_experience", "business", "technical"]
    
    # Create cache key
    cache_key = f"{product_category}_{'-'.join(agent_types)}_{max_discussion_rounds}_{disagreement_threshold}"
    
    # Check if coordinator exists in cache
    if cache_key not in coordinator_cache:
        coordinator_cache[cache_key] = LangGraphCoordinator(
            config=config,
            product_category=product_category,
            department_types=agent_types,
            max_tokens_per_department=max_tokens_per_agent,
            max_tokens_master=max_tokens_master,
            max_tokens_advisor=max_tokens_advisor,
            max_discussion_rounds=max_discussion_rounds,
            disagreement_threshold=disagreement_threshold
        )
    
    return coordinator_cache[cache_key]

@app.post("/rpc", response_model=JsonRpcResponse)
async def rpc_handler(rpc_req: JsonRpcRequest) -> JsonRpcResponse:
    """
    Handle JSON-RPC 2.0 requests for LangGraph multi-agent sentiment analysis.
    
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
                "max_tokens_master": 500,  # optional
                "max_tokens_advisor": 600,  # optional
                "max_discussion_rounds": 2,  # optional - LangGraph specific
                "disagreement_threshold": 0.6,  # optional - LangGraph specific
                "enable_consensus_debate": true  # optional - enable/disable debate
            }
        }
    }
    """
    
    # Validate basic RPC structure
    validation_error = validate_rpc_request(rpc_req)
    if validation_error:
        return validation_error
    
    try:
        # Extract task parameters
        task_id = rpc_req.params.get("id")
        message = rpc_req.params.get("message", {})
        metadata = rpc_req.params.get("metadata", {})
        
        # Extract text from message
        review_text = extract_text_from_message(message)
        if not review_text:
            return create_error_response(
                rpc_req.id, 
                -32602, 
                "Invalid params: No text content found in message"
            )
        
        # Extract configuration from metadata
        product_category = metadata.get("product_category", "electronics")
        agent_types = metadata.get("agent_types", ["quality", "experience", "user_experience", "business", "technical"])
        max_tokens_per_agent = metadata.get("max_tokens_per_agent", 150)
        max_tokens_master = metadata.get("max_tokens_master", 500)
        max_tokens_advisor = metadata.get("max_tokens_advisor", 600)
        max_discussion_rounds = metadata.get("max_discussion_rounds", 2)
        disagreement_threshold = metadata.get("disagreement_threshold", 0.6)
        enable_consensus_debate = metadata.get("enable_consensus_debate", True)
        
        logger.info(f"Processing LangGraph analysis request for category: {product_category}")
        logger.info(f"Agent types: {agent_types}")
        logger.info(f"Discussion config: max_rounds={max_discussion_rounds}, threshold={disagreement_threshold}")
        
        # Create or get coordinator
        coordinator = create_langgraph_coordinator(
            product_category=product_category,
            agent_types=agent_types,
            max_tokens_per_agent=max_tokens_per_agent,
            max_tokens_master=max_tokens_master,
            max_tokens_advisor=max_tokens_advisor,
            max_discussion_rounds=max_discussion_rounds,
            disagreement_threshold=disagreement_threshold
        )
        
        # Run LangGraph analysis
        if enable_consensus_debate:
            # Use the full LangGraph workflow with consensus and debate
            result = coordinator.run_analysis(review_text, task_id or "unknown")
        else:
            # Use simple analyze function without debate (fallback)
            result = analyze_with_langgraph(
                review=review_text,
                product_category=product_category,
                config=config,
                department_types=agent_types,
                max_discussion_rounds=0,  # Disable discussion
                disagreement_threshold=1.0  # Never trigger discussion
            )
        
        # Transform to A2A consensus format (as JSON string)
        a2a_result = transform_to_a2a_consensus_format(result, agent_types)
        
        logger.info(f"LangGraph analysis completed successfully")
        
        # Return A2A-compliant response format (matching POC)
        return {
            "jsonrpc": "2.0",
            "id": rpc_req.id,
            "result": {
                "id": task_id,
                "sessionId": f"langgraph-session-{task_id}",
                "status": {"state": "completed"},
                "artifacts": [
                    {
                        "parts": [
                            {"type": "text", "text": {"raw": a2a_result}}
                        ],
                        "index": 0,
                        "append": False,
                        "lastChunk": True
                    }
                ],
                "metadata": {
                    "agent_type": "langgraph_coordinator",
                    "product_category": product_category,
                    "workflow_type": "consensus_debate" if enable_consensus_debate else "standard",
                    "discussion_rounds": result.get("workflow_metadata", {}).get("discussion_rounds", 0),
                    "consensus_reached": result.get("workflow_metadata", {}).get("consensus_reached", True),
                    "disagreement_level": result.get("workflow_metadata", {}).get("disagreement_level", 0.0),
                    "total_agents": len(agent_types),
                    "processing_time": result.get("workflow_metadata", {}).get("processing_time", 0.0)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error in LangGraph coordinator: {str(e)}")
        return create_error_response(
            rpc_req.id,
            -32603,
            f"Internal error: {str(e)}"
        )

def transform_to_a2a_consensus_format(result: Dict[str, Any], agent_types: List[str]) -> str:
    """Transform LangGraph result to A2A consensus format with debate information"""
    import json
    
    # Extract consensus information
    consensus = {
        "overall_sentiment": result.get("master_analysis", {}).get("sentiment", "unknown"),
        "overall_confidence": result.get("master_analysis", {}).get("confidence", 0.0),
        "agreement_level": "high" if result.get("workflow_metadata", {}).get("consensus_reached", True) else "low",
        "key_insights": result.get("master_analysis", {}).get("reasoning", "No insights available"),
        "business_recommendations": result.get("business_recommendations", {}).get("business_impact", "No recommendations available")
    }
    
    # Extract individual agent analyses
    agent_analyses = []
    for analysis in result.get("department_analyses", []):
        agent_analyses.append({
            "agent_type": analysis.get("agent_type", "unknown"),
            "sentiment": analysis.get("sentiment", "unknown"),
            "confidence": analysis.get("confidence", 0.0),
            "emotions": analysis.get("emotions", []),
            "topics": analysis.get("topics", []),
            "reasoning": analysis.get("reasoning", "No reasoning"),
            "business_impact": analysis.get("business_impact", "No impact assessment")
        })
    
    # Extract discussion/debate information (unique to LangGraph)
    discussion_info = {
        "discussion_messages": result.get("discussion_messages", []),
        "discussion_rounds": result.get("workflow_metadata", {}).get("discussion_rounds", 0),
        "disagreement_level": result.get("workflow_metadata", {}).get("disagreement_level", 0.0),
        "consensus_reached": result.get("workflow_metadata", {}).get("consensus_reached", True)
    }
    
    # Metadata about the analysis
    analysis_metadata = {
        "total_agents": len(agent_types),
        "discussion_rounds": result.get("workflow_metadata", {}).get("discussion_rounds", 0),
        "average_confidence": sum(a.get("confidence", 0.0) for a in agent_analyses) / len(agent_analyses) if agent_analyses else 0.0,
        "agreement_score": 1.0 - result.get("workflow_metadata", {}).get("disagreement_level", 0.0),
        "analysis_duration": result.get("workflow_metadata", {}).get("processing_time", 0.0),
        "workflow_type": "langgraph_consensus_debate",
        "consensus_algorithm": "disagreement_threshold",
        "agents_participated": [a.get("agent_type") for a in agent_analyses]
    }
    
    # Create comprehensive A2A result
    a2a_consensus_result = {
        "consensus": consensus,
        "agent_analyses": agent_analyses,
        "discussion_info": discussion_info,
        "analysis_metadata": analysis_metadata,
        "review_text": result.get("review_text", ""),
        "product_category": result.get("product_category", "unknown")
    }
    
    return json.dumps(a2a_consensus_result, indent=2)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "langgraph_coordinator",
        "version": "1.0.0",
        "features": [
            "multi_agent_consensus",
            "agent_debate_discussion", 
            "disagreement_detection",
            "consensus_building",
            "a2a_protocol_compliant"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("LANGGRAPH_COORDINATOR_PORT", "8010"))
    
    print(f"🚀 Starting LangGraph Multi-Agent Coordinator RPC Server on port {port}")
    print(f"🔗 Agent Card: http://localhost:{port}/.well-known/agent.json")
    print(f"❤️ Health Check: http://localhost:{port}/health")
    print(f"🤖 RPC Endpoint: http://localhost:{port}/rpc")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
