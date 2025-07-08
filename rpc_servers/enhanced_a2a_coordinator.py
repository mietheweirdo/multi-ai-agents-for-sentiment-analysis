# rpc_servers/enhanced_a2a_coordinator.py
"""
Enhanced A2A Coordinator Agent - Uses A2A protocol for ALL inter-agent communication
This demonstrates true Agent-to-Agent communication using JSON-RPC
"""

import os
import logging
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add parent directory to path for module imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    title="Enhanced A2A Coordinator Agent",
    description="True A2A coordinator using JSON-RPC for all inter-agent communication",
    version="2.0.0"
)

# Setup agent card endpoint
setup_agent_card_endpoint(
    app, 
    os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards", "enhanced_coordinator_card.json")
)

# A2A Agent endpoints
AGENT_ENDPOINTS = {
    "quality": f"http://localhost:{os.getenv('QUALITY_AGENT_PORT', '8001')}/rpc",
    "experience": f"http://localhost:{os.getenv('EXPERIENCE_AGENT_PORT', '8002')}/rpc",
    "user_experience": f"http://localhost:{os.getenv('USER_EXPERIENCE_AGENT_PORT', '8003')}/rpc",
    "business": f"http://localhost:{os.getenv('BUSINESS_AGENT_PORT', '8004')}/rpc",
    "technical": f"http://localhost:{os.getenv('TECHNICAL_AGENT_PORT', '8005')}/rpc"
}

class A2ACoordinator:
    """
    Enhanced coordinator that uses A2A protocol for all inter-agent communication
    """
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_a2a_payload(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create A2A JSON-RPC payload for agent communication"""
        import uuid
        task_id = str(uuid.uuid4())
        
        return {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "message": {
                    "role": "coordinator",
                    "parts": [{"type": "text", "text": text}]
                },
                "metadata": metadata or {}
            }
        }
    
    async def call_agent_a2a(self, agent_type: str, review_text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call an agent using A2A protocol"""
        endpoint = AGENT_ENDPOINTS.get(agent_type)
        if not endpoint:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        payload = self.create_a2a_payload(review_text, metadata)
        
        try:
            logger.info(f"📞 A2A call to {agent_type} agent at {endpoint}")
            
            async with self.session.post(endpoint, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if "result" in result:
                        # Extract agent response
                        result_text = result["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
                        agent_data = json.loads(result_text)
                        
                        logger.info(f"✅ {agent_type} agent responded: {agent_data.get('sentiment', 'unknown')}")
                        return {
                            'success': True,
                            'agent_type': agent_type,
                            'data': agent_data
                        }
                    else:
                        error_msg = result.get('error', {}).get('message', 'Unknown error')
                        logger.error(f"❌ {agent_type} agent error: {error_msg}")
                        return {
                            'success': False,
                            'agent_type': agent_type,
                            'error': error_msg
                        }
                else:
                    logger.error(f"❌ {agent_type} agent HTTP error: {response.status}")
                    return {
                        'success': False,
                        'agent_type': agent_type,
                        'error': f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"❌ {agent_type} agent call failed: {e}")
            return {
                'success': False,
                'agent_type': agent_type,
                'error': str(e)
            }
    
    async def coordinate_multi_agent_analysis(self, review_text: str, agent_types: List[str], product_category: str = "electronics") -> Dict[str, Any]:
        """
        Coordinate multi-agent analysis using A2A protocol
        
        This is TRUE Agent-to-Agent communication - each agent runs independently
        and communicates via JSON-RPC A2A protocol
        """
        logger.info(f"🚀 Starting A2A multi-agent analysis with {len(agent_types)} agents")
        
        # Prepare metadata for agents
        agent_metadata = {
            "product_category": product_category,
            "max_tokens": 150,
            "coordinator_session": "a2a_multi_agent",
            "analysis_type": "sentiment_analysis"
        }
        
        # Step 1: Call all department agents in parallel using A2A
        logger.info("📞 Phase 1: Calling department agents via A2A...")
        
        tasks = []
        for agent_type in agent_types:
            task = self.call_agent_a2a(agent_type, review_text, agent_metadata)
            tasks.append(task)
        
        # Execute all agent calls in parallel
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_analyses = []
        failed_agents = []
        
        for result in agent_results:
            if isinstance(result, Exception):
                failed_agents.append(f"Exception: {result}")
            elif result.get('success'):
                successful_analyses.append(result['data'])
            else:
                failed_agents.append(f"{result.get('agent_type', 'unknown')}: {result.get('error', 'unknown error')}")
        
        logger.info(f"✅ A2A Phase 1 complete: {len(successful_analyses)} successful, {len(failed_agents)} failed")
        
        if not successful_analyses:
            return {
                'success': False,
                'error': 'All department agents failed',
                'failed_agents': failed_agents
            }
        
        # Step 2: Create master analysis from department results
        logger.info("🧠 Phase 2: Generating master analysis...")
        
        master_analysis = self._create_master_analysis(successful_analyses, review_text)
        
        # Step 3: Generate business recommendations
        logger.info("💼 Phase 3: Generating business recommendations...")
        
        business_recommendations = self._create_business_recommendations(master_analysis, successful_analyses, review_text)
        
        # Step 4: Compile final result
        final_result = {
            'success': True,
            'department_analyses': successful_analyses,
            'master_analysis': master_analysis,
            'business_recommendations': business_recommendations,
            'workflow_metadata': {
                'total_agents_called': len(agent_types),
                'successful_agents': len(successful_analyses),
                'failed_agents': len(failed_agents),
                'communication_protocol': 'A2A JSON-RPC',
                'parallel_execution': True,
                'coordinator_version': '2.0.0'
            }
        }
        
        if failed_agents:
            final_result['workflow_metadata']['failed_agents_details'] = failed_agents
        
        logger.info("🎉 A2A multi-agent analysis complete!")
        return final_result
    
    def _create_master_analysis(self, department_analyses: List[Dict], review_text: str) -> Dict[str, Any]:
        """Create master analysis from department results"""
        
        # Aggregate sentiments
        sentiments = [analysis.get('sentiment', 'neutral') for analysis in department_analyses]
        confidences = [analysis.get('confidence', 0.0) for analysis in department_analyses]
        
        # Calculate overall sentiment
        sentiment_counts = {}
        for sentiment in sentiments:
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Most common sentiment
        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Create reasoning
        dept_summaries = []
        for analysis in department_analyses:
            agent_type = analysis.get('agent_type', 'unknown')
            sentiment = analysis.get('sentiment', 'neutral')
            dept_summaries.append(f"{agent_type}: {sentiment}")
        
        reasoning = f"Based on analysis from {len(department_analyses)} departments ({', '.join(dept_summaries)}), the overall sentiment is {overall_sentiment}."
        
        return {
            'sentiment': overall_sentiment,
            'confidence': overall_confidence,
            'reasoning': reasoning,
            'department_consensus': sentiment_counts,
            'analysis_method': 'A2A Multi-Agent Consensus'
        }
    
    def _create_business_recommendations(self, master_analysis: Dict, department_analyses: List[Dict], review_text: str) -> Dict[str, Any]:
        """Create business recommendations from analysis results"""
        
        # Collect insights from all departments
        all_emotions = []
        all_topics = []
        key_insights = []
        
        for analysis in department_analyses:
            emotions = analysis.get('emotions', [])
            topics = analysis.get('topics', [])
            reasoning = analysis.get('reasoning', '')
            
            all_emotions.extend(emotions)
            all_topics.extend(topics)
            
            if reasoning:
                key_insights.append(f"{analysis.get('agent_type', 'Agent')}: {reasoning[:100]}...")
        
        # Remove duplicates
        unique_emotions = list(set(all_emotions))[:5]
        unique_topics = list(set(all_topics))[:5]
        
        # Generate business impact
        overall_sentiment = master_analysis.get('sentiment', 'neutral')
        confidence = master_analysis.get('confidence', 0.0)
        
        if overall_sentiment == 'positive':
            business_impact = f"Your product is performing well with {confidence:.0%} positive sentiment. Focus on maintaining quality and expanding successful features. Key areas: {', '.join(unique_topics[:3])}."
        elif overall_sentiment == 'negative':
            business_impact = f"Immediate attention needed - {confidence:.0%} negative sentiment detected. Priority actions: address customer concerns about {', '.join(unique_topics[:3])}. Customer emotions show: {', '.join(unique_emotions[:3])}."
        else:
            business_impact = f"Mixed customer feedback with {confidence:.0%} confidence. Opportunities for improvement in: {', '.join(unique_topics[:3])}. Focus on addressing: {', '.join(unique_emotions[:3])}."
        
        reasoning = f"This recommendation is based on A2A analysis from {len(department_analyses)} specialized agents, providing comprehensive coverage of quality, experience, and business perspectives."
        
        return {
            'sentiment': overall_sentiment,
            'confidence': confidence,
            'emotions': unique_emotions,
            'topics': unique_topics,
            'business_impact': business_impact,
            'reasoning': reasoning,
            'key_insights': key_insights,
            'recommendation_method': 'A2A Multi-Agent Business Analysis'
        }

# Global coordinator instance
coordinator = A2ACoordinator()

@app.post("/rpc", response_model=JsonRpcResponse)
async def rpc_handler(rpc_req: JsonRpcRequest) -> JsonRpcResponse:
    """
    Handle JSON-RPC requests using A2A protocol for inter-agent communication
    """
    logger.info(f"Received A2A coordination request: {rpc_req.method}")
    
    # Validate request
    error_response = validate_rpc_request(rpc_req)
    if error_response:
        return error_response
    
    try:
        # Extract input
        message = rpc_req.params["message"]
        input_text = extract_text_from_message(message)
        
        # Get metadata
        metadata = rpc_req.params.get("metadata", {})
        product_category = metadata.get("product_category", "electronics")
        agent_types = metadata.get("agent_types", ["quality", "experience", "user_experience", "business"])
        
        # Handle scraping if requested (same as before)
        enable_scraping = metadata.get("enable_scraping", False)
        product_name = metadata.get("product_name", None)
        
        if enable_scraping and product_name:
            logger.info(f"🔍 Auto-scraping enabled for: {product_name}")
            try:
                from data_pipeline import scrape_and_preprocess
                
                scraped_data = scrape_and_preprocess(
                    keyword=product_name,
                    sources=metadata.get("sources", ["youtube", "tiki"]),
                    max_items_per_source=metadata.get("max_items_per_source", 5)
                )
                
                if scraped_data:
                    from rpc_servers.coordinator_agent_rpc import combine_scraped_reviews
                    review_text, scraping_metadata = combine_scraped_reviews(scraped_data, product_name)
                    if scraped_data[0].get('product_category'):
                        product_category = scraped_data[0]['product_category']
                else:
                    review_text = f"No reviews found for {product_name}."
                    scraping_metadata = {}
                    
            except Exception as e:
                logger.error(f"Scraping failed: {e}")
                review_text = input_text
        else:
            review_text = input_text
            scraping_metadata = {}  # No scraping metadata for direct text
        
        # Run A2A multi-agent analysis
        async with coordinator:
            result = await coordinator.coordinate_multi_agent_analysis(
                review_text=review_text,
                agent_types=agent_types,
                product_category=product_category
            )
        
        # Add scraping metadata to workflow metadata if available
        if scraping_metadata:
            if 'workflow_metadata' not in result:
                result['workflow_metadata'] = {}
            result['workflow_metadata']['scraping_metadata'] = scraping_metadata
        
        if result['success']:
            # Format result
            output_text = json.dumps(result, indent=2)
            
            master_analysis = result.get('master_analysis', {})
            overall_sentiment = master_analysis.get('sentiment', 'unknown')
            overall_confidence = master_analysis.get('confidence', 0.0)
            
            logger.info(f"🎉 A2A coordination complete: {overall_sentiment} ({overall_confidence:.1%})")
            
            return create_a2a_response(
                request_id=rpc_req.id,
                task_id=rpc_req.params.get("id"),
                output_text=output_text,
                session_id=f"a2a-coord-{rpc_req.params.get('id', 'unknown')[:8]}",
                metadata={
                    "agent_type": "a2a_coordinator",
                    "communication_protocol": "A2A JSON-RPC",
                    "product_category": product_category,
                    "agents_used": agent_types,
                    "overall_sentiment": overall_sentiment,
                    "overall_confidence": overall_confidence,
                    "total_agents": len(agent_types),
                    "successful_agents": result.get('workflow_metadata', {}).get('successful_agents', 0)
                }
            )
        else:
            return create_error_response(
                rpc_req.id,
                -32603,
                f"A2A coordination failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"A2A coordination failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_error_response(
            rpc_req.id,
            -32603,
            f"A2A coordination failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "a2a_coordinator",
        "version": "2.0.0",
        "communication_protocol": "A2A JSON-RPC",
        "available_agents": list(AGENT_ENDPOINTS.keys()),
        "features": ["parallel_a2a_calls", "async_coordination", "true_agent_to_agent"]
    }

@app.get("/agents")
async def list_agents():
    """List available agents and their A2A endpoints"""
    return {
        "total_agents": len(AGENT_ENDPOINTS),
        "agents": AGENT_ENDPOINTS,
        "communication_method": "A2A JSON-RPC 2.0",
        "parallel_execution": True
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("A2A_COORDINATOR_PORT", "8020"))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    reload = os.getenv("FASTAPI_RELOAD", "false").lower() == "true"
    
    logger.info(f"🚀 Starting Enhanced A2A Coordinator on {host}:{port}")
    logger.info(f"📞 Will use A2A protocol to communicate with {len(AGENT_ENDPOINTS)} agents")
    uvicorn.run(
        "enhanced_a2a_coordinator:app",
        host=host,
        port=port,
        reload=reload
    ) 