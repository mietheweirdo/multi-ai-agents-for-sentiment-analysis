# agents/sentiment_agents.py
import json
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Import the new organized prompt structure
from .prompts import AgentPrompts, ProductPrompts, BasePrompts

class SentimentResult(BaseModel):
    sentiment: str = Field(description="Overall sentiment: positive, neutral, or negative")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    emotions: List[str] = Field(description="List of emotions detected")
    topics: List[str] = Field(description="Key topics/facets mentioned")
    reasoning: str = Field(description="Brief reasoning for sentiment (max 100 words)")
    business_impact: str = Field(description="Business impact assessment (max 50 words)")

class BaseSentimentAgent:
    """Base class for specialized sentiment analysis agents"""
    
    def __init__(self, config: Dict[str, Any], agent_type: str, max_tokens: int = 150, product_category: str = "electronics"):
        self.config = config
        self.agent_type = agent_type
        self.max_tokens = max_tokens
        self.product_category = product_category
        self.model_name = config.get("model_name", "gpt-4o-mini")
        self.api_key = config.get("api_key")
        
        # Initialize LLM with token limits
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            max_tokens=self.max_tokens,
            temperature=0.1  # Low temperature for consistent analysis
        )
        
        # Initialize output parser
        self.output_parser = JsonOutputParser(pydantic_object=SentimentResult)
        
        # Get agent-specific prompt and customize for product category
        base_prompt = AgentPrompts.get_agent_prompt(agent_type, max_tokens)
        customized_prompt = ProductPrompts.customize_agent_prompt(
            base_prompt, product_category, agent_type
        )
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", customized_prompt),
            ("human", BasePrompts.HUMAN_TEMPLATE)
        ])
        
        # Create chain
        self.chain = self.prompt | self.llm | self.output_parser
    
    def analyze(self, review: str) -> Dict[str, Any]:
        """Analyze a single review"""
        try:
            result = self.chain.invoke({"review": review})
            # Format and validate the output
            formatted_result = BasePrompts.format_agent_output(result)
            formatted_result['agent_type'] = self.agent_type
            formatted_result['agent_name'] = self.__class__.__name__
            return formatted_result
        except Exception as e:
            print(f"[{self.__class__.__name__}] Error analyzing review: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [],
                "topics": [],
                "reasoning": f"Analysis error: {str(e)}",
                "business_impact": "Unable to assess",
                "agent_type": self.agent_type,
                "agent_name": self.__class__.__name__
            }

class ProductQualityAgent(BaseSentimentAgent):
    """Specialized agent for analyzing product quality aspects"""
    
    def __init__(self, config: Dict[str, Any], max_tokens: int = 150, product_category: str = "electronics"):
        super().__init__(config, "quality", max_tokens, product_category)

class CustomerExperienceAgent(BaseSentimentAgent):
    """Specialized agent for analyzing customer service and delivery experience"""
    
    def __init__(self, config: Dict[str, Any], max_tokens: int = 150, product_category: str = "electronics"):
        super().__init__(config, "experience", max_tokens, product_category)

class UserExperienceAgent(BaseSentimentAgent):
    """Specialized agent for analyzing user experience and emotional response"""
    
    def __init__(self, config: Dict[str, Any], max_tokens: int = 150, product_category: str = "electronics"):
        super().__init__(config, "user_experience", max_tokens, product_category)

class BusinessImpactAgent(BaseSentimentAgent):
    """Specialized agent for analyzing business impact and market implications"""
    
    def __init__(self, config: Dict[str, Any], max_tokens: int = 150, product_category: str = "electronics"):
        super().__init__(config, "business", max_tokens, product_category)

class TechnicalSpecAgent(BaseSentimentAgent):
    """Specialized agent for analyzing technical specifications and features"""
    
    def __init__(self, config: Dict[str, Any], max_tokens: int = 150, product_category: str = "electronics"):
        super().__init__(config, "technical", max_tokens, product_category)

# Agent factory for easy creation
class SentimentAgentFactory:
    """Factory for creating specialized sentiment analysis agents"""
    
    @staticmethod
    def create_agent(agent_type: str, config: Dict[str, Any], max_tokens: int = 150, product_category: str = "electronics") -> BaseSentimentAgent:
        """Create a specialized agent based on type"""
        
        agent_classes = {
            "quality": ProductQualityAgent,
            "experience": CustomerExperienceAgent,
            "user_experience": UserExperienceAgent,
            "business": BusinessImpactAgent,
            "technical": TechnicalSpecAgent
        }
        
        if agent_type not in agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(agent_classes.keys())}")
        
        return agent_classes[agent_type](
            config=config,
            max_tokens=max_tokens,
            product_category=product_category
        )
    
    @staticmethod
    def create_agent_team(config: Dict[str, Any], agent_types: List[str] = None, max_tokens: int = 150, product_category: str = "electronics") -> List[BaseSentimentAgent]:
        """Create a team of specialized agents"""
        
        if agent_types is None:
            agent_types = ["quality", "experience", "user_experience", "business"]
        
        agents = []
        for agent_type in agent_types:
            agent = SentimentAgentFactory.create_agent(agent_type, config, max_tokens, product_category)
            agents.append(agent)
        
        return agents
    
    @staticmethod
    def get_available_agent_types() -> List[str]:
        """Get list of available agent types"""
        return AgentPrompts.get_available_agent_types()
    
    @staticmethod
    def get_agent_description(agent_type: str) -> str:
        """Get description of an agent type"""
        return AgentPrompts.get_agent_description(agent_type) 