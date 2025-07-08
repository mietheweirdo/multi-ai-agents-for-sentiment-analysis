# rpc_servers/coordinator_agent_rpc.py
"""
Coordinator Agent RPC Server - A2A compatible JSON-RPC endpoint
Orchestrates multi-agent sentiment analysis using your existing EnhancedCoordinatorAgent
"""

import os
import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for module imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import existing coordinator functionality
from workflow_manager import MultiAgentWorkflowManager
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

def combine_scraped_reviews(scraped_data: List[Dict], product_name: str) -> tuple[str, dict]:
    """Combine scraped reviews into single analysis dataset and return metadata"""
    combined_text = ""
    review_count = len(scraped_data)
    
    # Track metadata for response
    sources_used = set()
    reviews_by_source = {}
    sample_reviews = []
    
    # Add summary header
    combined_text += f"COMPREHENSIVE PRODUCT ANALYSIS DATASET\n"
    combined_text += f"Product: {product_name}\n"
    combined_text += f"Total Reviews: {review_count}\n"
    combined_text += f"Sources: {', '.join(set(item.get('metadata', {}).get('source', 'unknown') for item in scraped_data))}\n\n"
    
    # Add each review with clear separation
    for i, item in enumerate(scraped_data, 1):
        review = item.get('review_text', '')
        source = item.get('metadata', {}).get('source', 'unknown')
        
        # Track sources and counts
        sources_used.add(source)
        reviews_by_source[source] = reviews_by_source.get(source, 0) + 1
        
        # Collect sample reviews for display (first 3)
        if len(sample_reviews) < 3:
            sample_reviews.append({
                'source': source,
                'text': review
            })
        
        combined_text += f"REVIEW {i} (Source: {source.upper()}):\n"
        combined_text += f"{review}\n\n"
    
    # Add analysis instruction
    combined_text += f"""ANALYSIS INSTRUCTION:
Please analyze all {review_count} customer reviews above as a comprehensive dataset to provide:
1. Overall sentiment assessment for {product_name}
2. Detailed business recommendations for product improvement
3. Key insights from customer feedback
4. Actionable strategies to address customer concerns

Focus on providing specific, actionable business recommendations that can help improve the product based on real customer feedback."""
    
    # Create scraping metadata
    scraping_metadata = {
        'sources_scraped': list(sources_used),
        'total_reviews_collected': review_count,
        'reviews_by_source': reviews_by_source,
        'sample_reviews': sample_reviews
    }
    
    return combined_text, scraping_metadata

def create_coordinator(
    product_category: str = "electronics",
    agent_types: Optional[List[str]] = None,
    max_tokens_per_agent: int = 150,
    max_tokens_consensus: int = 800,
    max_rounds: int = 2
) -> MultiAgentWorkflowManager:
    """Create a coordinator with specified configuration"""
    
    if agent_types is None:
        agent_types = ["quality", "experience", "user_experience", "business"]
    
    return MultiAgentWorkflowManager(
        config=config,
        product_category=product_category,
        department_types=agent_types,
        max_tokens_per_department=max_tokens_per_agent,
        max_tokens_master=500,
        max_tokens_advisor=max_tokens_consensus
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
        input_text = extract_text_from_message(message)
        
        # Get optional parameters from metadata
        metadata = rpc_req.params.get("metadata", {})
        product_category = metadata.get("product_category", os.getenv("DEFAULT_PRODUCT_CATEGORY", "electronics"))
        agent_types = metadata.get("agent_types", ["quality", "experience", "user_experience", "business"])
        max_tokens_per_agent = metadata.get("max_tokens_per_agent", int(os.getenv("DEFAULT_MAX_TOKENS_PER_AGENT", "150")))
        max_tokens_consensus = metadata.get("max_tokens_consensus", int(os.getenv("DEFAULT_MAX_TOKENS_CONSENSUS", "800")))
        max_rounds = metadata.get("max_rounds", int(os.getenv("DEFAULT_MAX_ROUNDS", "2")))
        
        # Check for scraping request
        enable_scraping = metadata.get("enable_scraping", False)
        product_name = metadata.get("product_name", None)
        sources = metadata.get("sources", ["youtube", "tiki"])
        max_items_per_source = metadata.get("max_items_per_source", 5)
        
        logger.info(f"Coordinating sentiment analysis for category: {product_category}")
        logger.info(f"Agent types: {agent_types}")
        logger.info(f"Enable scraping: {enable_scraping}")
        if enable_scraping and product_name:
            logger.info(f"Product name: {product_name}")
            logger.info(f"Sources: {sources}")
        
        # Handle scraping if requested
        if enable_scraping and product_name:
            logger.info(f"Starting scraping pipeline for product: {product_name}")
            try:
                # Import scraping functionality
                from data_pipeline import scrape_and_preprocess
                
                # Scrape reviews
                scraped_data = scrape_and_preprocess(
                    keyword=product_name,
                    sources=sources,
                    max_items_per_source=max_items_per_source
                )
                
                if not scraped_data:
                    logger.warning(f"No reviews found for {product_name}")
                    review_text = f"No reviews found for {product_name}. Please try a different product name or check if the product exists on the specified platforms."
                else:
                    logger.info(f"Scraped {len(scraped_data)} reviews for {product_name}")
                    
                    # Combine reviews for comprehensive analysis
                    review_text, scraping_metadata = combine_scraped_reviews(scraped_data, product_name)
                    
                    # Update product category if detected from scraped data
                    if scraped_data and scraped_data[0].get('product_category'):
                        detected_category = scraped_data[0]['product_category']
                        logger.info(f"Detected product category: {detected_category}")
                        product_category = detected_category
                        
            except ImportError:
                logger.error("Data pipeline not available for scraping")
                review_text = "Data scraping functionality is not available. Please provide review text directly."
            except Exception as e:
                logger.error(f"Scraping failed: {e}")
                review_text = f"Failed to scrape reviews for {product_name}: {str(e)}. Please provide review text directly."
        else:
            # Use provided text directly
            review_text = input_text
            scraping_metadata = {}  # No scraping metadata for direct text
        
        logger.info(f"Analysis input text: {review_text[:100]}...")
        
        # Create or reconfigure coordinator if needed
        if (coordinator is None or 
            coordinator.product_category != product_category or
            len(coordinator.department_agents) != len(agent_types) or
            coordinator.max_tokens_per_department != max_tokens_per_agent):
            
            logger.info("Creating new coordinator with specified configuration")
            coordinator = create_coordinator(
                product_category=product_category,
                agent_types=agent_types,
                max_tokens_per_agent=max_tokens_per_agent,
                max_tokens_consensus=max_tokens_consensus,
                max_rounds=max_rounds
            )
        
        # Run coordinated analysis using your existing workflow
        analysis_result = coordinator.run_analysis(review_text)
        
        # Add scraping metadata to workflow metadata if available
        if scraping_metadata:
            if 'workflow_metadata' not in analysis_result:
                analysis_result['workflow_metadata'] = {}
            analysis_result['workflow_metadata']['scraping_metadata'] = scraping_metadata
        
        # Format result as JSON string for A2A response
        import json
        output_text = json.dumps(analysis_result, indent=2)
        
        # Extract key metrics for metadata
        master_analysis = analysis_result.get('master_analysis', {})
        overall_sentiment = master_analysis.get('sentiment', 'unknown')
        overall_confidence = master_analysis.get('confidence', 0.0)
        
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
                "processing_time": analysis_result.get('workflow_metadata', {}).get('processing_time', 0)
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
        "agent_types": coordinator.department_types,
        "max_tokens_per_agent": coordinator.max_tokens_per_department,
        "max_tokens_consensus": coordinator.max_tokens_advisor,
        "max_rounds": 3,  # Default for 3-layer system
        "total_agents": len(coordinator.department_agents)
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
