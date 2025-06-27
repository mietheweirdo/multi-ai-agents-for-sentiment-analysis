# enhanced_a2a_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from agents.enhanced_coordinator import EnhancedCoordinatorAgent
from agents.product_prompts import ProductPromptManager

app = FastAPI(
    title="Enhanced Multi-Agent Sentiment Analysis API",
    description="Advanced sentiment analysis using specialized AI agents with product-specific prompts",
    version="2.0.0"
)

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

# Global coordinator instance
coordinator = None

class AnalysisRequest(BaseModel):
    reviews: List[str]
    product_category: str = "electronics"
    agent_types: Optional[List[str]] = None
    max_tokens_per_agent: int = 150
    max_tokens_consensus: int = 800  # Added parameter for consensus token limit
    product_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    message: str

class CategoryInfo(BaseModel):
    category: str
    description: str
    available_agents: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced coordinator on startup"""
    global coordinator
    coordinator = EnhancedCoordinatorAgent(
        config=CONFIG,
        product_category="electronics",
        max_tokens_per_agent=150
    )
    print("🚀 Enhanced Multi-Agent Sentiment Analysis API started")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Enhanced Multi-Agent Sentiment Analysis API",
        "version": "2.0.0",
        "description": "Advanced sentiment analysis using specialized AI agents",
        "features": [
            "Product-specific analysis",
            "Token-optimized responses",
            "Multi-agent consensus",
            "Specialized agent roles"
        ]
    }

@app.get("/categories", response_model=List[CategoryInfo])
async def get_categories():
    """Get available product categories and their descriptions"""
    categories = ProductPromptManager.get_available_categories()
    
    category_info = []
    for category in categories:
        description = ProductPromptManager.get_category_description(category)
        available_agents = ["quality", "experience", "user_experience", "business", "technical"]
        
        category_info.append(CategoryInfo(
            category=category,
            description=description,
            available_agents=available_agents
        ))
    
    return category_info

@app.get("/agents")
async def get_agents():
    """Get information about available agent types"""
    return {
        "quality": {
            "name": "Product Quality Specialist",
            "description": "Analyzes product quality, materials, durability, and manufacturing aspects",
            "focus": "Quality and craftsmanship"
        },
        "experience": {
            "name": "Customer Experience Specialist", 
            "description": "Analyzes customer service, delivery, and post-purchase experience",
            "focus": "Service and logistics"
        },
        "user_experience": {
            "name": "User Experience Specialist",
            "description": "Analyzes emotional responses, design, and user satisfaction",
            "focus": "Emotions and satisfaction"
        },
        "business": {
            "name": "Business Intelligence Analyst",
            "description": "Analyzes market impact, competitive positioning, and business implications",
            "focus": "Business and market impact"
        },
        "technical": {
            "name": "Technical Product Specialist",
            "description": "Analyzes technical specifications, features, and performance",
            "focus": "Technical aspects and features"
        }
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_sentiment(request: AnalysisRequest):
    """Analyze sentiment using enhanced multi-agent system"""
    global coordinator
    
    try:
        # Update coordinator configuration if needed
        if request.product_category != coordinator.product_category:
            coordinator.change_product_category(request.product_category)
        
        # Set agent types if specified
        if request.agent_types:
            # Recreate coordinator with new agent types
            coordinator = EnhancedCoordinatorAgent(
                config=CONFIG,
                product_category=request.product_category,
                agent_types=request.agent_types,
                max_tokens_per_agent=request.max_tokens_per_agent,
                max_tokens_consensus=request.max_tokens_consensus
            )
        
        # Run analysis
        result = coordinator.run_workflow(
            reviews=request.reviews,
            product_category=request.product_category
        )
        
        return AnalysisResponse(
            success=True,
            data=result,
            metadata={
                "product_category": request.product_category,
                "agent_types": request.agent_types or ["quality", "experience", "user_experience", "business"],
                "max_tokens_per_agent": request.max_tokens_per_agent,
                "max_tokens_consensus": request.max_tokens_consensus,
                "total_reviews": len(request.reviews)
            },
            message="Analysis completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/single")
async def analyze_single_review(review: str, product_category: str = "electronics"):
    """Analyze a single review with default settings"""
    global coordinator
    
    try:
        # Ensure coordinator is set to correct category
        if product_category != coordinator.product_category:
            coordinator.change_product_category(product_category)
        
        result = coordinator.run_workflow(
            reviews=[review],
            product_category=product_category
        )
        
        return {
            "success": True,
            "review": review,
            "analysis": result,
            "product_category": product_category
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global coordinator
    
    return {
        "status": "healthy",
        "coordinator_initialized": coordinator is not None,
        "product_category": coordinator.product_category if coordinator else None,
        "available_categories": ProductPromptManager.get_available_categories()
    }

@app.get("/config")
async def get_config():
    """Get current configuration (without sensitive data)"""
    return {
        "model_name": CONFIG.get("model_name"),
        "product_category": coordinator.product_category if coordinator else None,
        "max_tokens_per_agent": coordinator.max_tokens_per_agent if coordinator else None,
        "available_categories": ProductPromptManager.get_available_categories()
    }

@app.post("/config/update")
async def update_config(
    product_category: Optional[str] = None,
    max_tokens_per_agent: Optional[int] = None,
    agent_types: Optional[List[str]] = None
):
    """Update coordinator configuration"""
    global coordinator
    
    try:
        if product_category:
            coordinator.change_product_category(product_category)
        
        if max_tokens_per_agent or agent_types:
            # Recreate coordinator with new settings
            coordinator = EnhancedCoordinatorAgent(
                config=CONFIG,
                product_category=coordinator.product_category,
                agent_types=agent_types or coordinator.sentiment_agents,
                max_tokens_per_agent=max_tokens_per_agent or coordinator.max_tokens_per_agent
            )
        
        return {
            "success": True,
            "message": "Configuration updated",
            "current_config": {
                "product_category": coordinator.product_category,
                "max_tokens_per_agent": coordinator.max_tokens_per_agent,
                "agent_types": [coordinator._get_agent_type(agent) for agent in coordinator.sentiment_agents]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Configuration update failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 