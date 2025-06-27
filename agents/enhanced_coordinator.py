# agents/enhanced_coordinator.py
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import Counter
import statistics
from datetime import datetime

from agents.scraper import ScraperAgent
from agents.preprocessor import PreprocessorAgent
from agents.memory_manager import MemoryManagerAgent
from agents.reporter import ReporterAgent
from agents.sentiment_agents import SentimentAgentFactory, BaseSentimentAgent
# Import the new organized prompt structure
from agents.prompts import CoordinatorPrompts, ProductPrompts
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

@dataclass
class EnhancedAnalysisState:
    """State for enhanced multi-agent sentiment analysis"""
    review: Dict[str, Any]
    agent_outputs: List[Dict[str, Any]] = field(default_factory=list)
    consensus: Dict[str, Any] = field(default_factory=dict)
    discussion_history: List[Dict[str, Any]] = field(default_factory=list)
    round: int = 0
    product_category: str = "electronics"
    confidence_scores: List[float] = field(default_factory=list)

class EnhancedCoordinatorAgent:
    """Enhanced coordinator with specialized agents and product-specific prompts"""
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None, 
                 product_category: str = "electronics",
                 agent_types: Optional[List[str]] = None,
                 max_tokens_per_agent: int = 150,
                 max_rounds: int = 2,
                 max_tokens_consensus: int = 800):
        
        # Load config
        if config is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        self.config = config
        self.product_category = product_category
        self.max_tokens_per_agent = max_tokens_per_agent
        self.max_rounds = max_rounds
        self.max_tokens_consensus = max_tokens_consensus
        
        # Initialize agents
        self.scraper = ScraperAgent()
        self.preprocessor = PreprocessorAgent(use_llm=False, config=self.config)
        self.memory = MemoryManagerAgent()
        self.reporter = ReporterAgent(config=self.config)
        
        # Create specialized sentiment agents with product category
        if agent_types is None:
            agent_types = ["quality", "experience", "user_experience", "business"]
        
        self.sentiment_agents = SentimentAgentFactory.create_agent_team(
            config=self.config,
            agent_types=agent_types,
            max_tokens=max_tokens_per_agent,
            product_category=product_category
        )
        
        # Initialize consensus LLM with configurable token limit
        self.consensus_llm = ChatOpenAI(
            model=self.config.get("model_name", "gpt-4o-mini"),
            api_key=self.config.get("api_key"),
            max_tokens=max_tokens_consensus,
            temperature=0.1
        )
        
        # Build LangGraph workflow
        self.graph = self._build_enhanced_workflow()
        
        print(f"[EnhancedCoordinator] Initialized for {product_category} products with {len(self.sentiment_agents)} agents")
        print(f"[EnhancedCoordinator] Token limit per agent: {max_tokens_per_agent}")
        print(f"[EnhancedCoordinator] Token limit for consensus: {max_tokens_consensus}")
        print(f"[EnhancedCoordinator] Available categories: {ProductPrompts.get_available_categories()}")
    
    def _build_enhanced_workflow(self):
        """Build enhanced LangGraph workflow with better consensus and discussion"""
        
        g = StateGraph(EnhancedAnalysisState)
        
        def analyze_step(state: EnhancedAnalysisState):
            """Initial analysis step - all agents analyze the review"""
            review_text = state.review.get('cleaned_text', state.review.get('text', ''))
            print(f"\n[EnhancedCoordinator] Analyzing review: {review_text[:100]}...")
            
            outputs = []
            confidence_scores = []
            
            for i, agent in enumerate(self.sentiment_agents):
                agent_type = agent.agent_type
                print(f"[EnhancedCoordinator] {agent_type} agent analyzing...")
                
                try:
                    result = agent.analyze(review_text)
                    outputs.append(result)
                    confidence_scores.append(result.get('confidence', 0.5))
                    
                    print(f"[EnhancedCoordinator] {agent_type}: {result['sentiment']} (confidence: {result['confidence']:.2f})")
                    
                except Exception as e:
                    print(f"[EnhancedCoordinator] {agent_type} agent error: {e}")
                    fallback_result = {
                        'sentiment': 'neutral',
                        'confidence': 0.5,
                        'emotions': [],
                        'topics': [],
                        'reasoning': f"Error: {str(e)}",
                        'business_impact': "Unable to assess",
                        'agent_type': agent_type,
                        'agent_name': agent.__class__.__name__
                    }
                    outputs.append(fallback_result)
                    confidence_scores.append(0.5)
            
            return EnhancedAnalysisState(
                review=state.review,
                agent_outputs=outputs,
                consensus={},
                discussion_history=[],
                round=0,
                product_category=state.product_category,
                confidence_scores=confidence_scores
            )
        
        def discussion_step(state: EnhancedAnalysisState):
            """Discussion step - agents can revise based on others' analysis"""
            print(f"\n[EnhancedCoordinator] Discussion round {state.round + 1}")
            
            discussion_history = state.discussion_history.copy()
            new_outputs = []
            new_confidence_scores = []
            
            # Create context from other agents' analysis
            other_analyses = []
            for output in state.agent_outputs:
                other_analyses.append({
                    'agent_type': output['agent_type'],
                    'sentiment': output['sentiment'],
                    'confidence': output['confidence'],
                    'reasoning': output['reasoning']
                })
            
            for i, agent in enumerate(state.agent_outputs):
                agent_type = agent['agent_type']
                current_sentiment = agent['sentiment']
                current_confidence = agent['confidence']
                
                # Check if consensus is needed
                sentiments = [o['sentiment'] for o in state.agent_outputs]
                sentiment_counts = Counter(sentiments)
                
                if len(set(sentiments)) > 1 and state.round < self.max_rounds:
                    # Agents disagree - add discussion entry
                    discussion_entry = {
                        'round': state.round + 1,
                        'agent_type': agent_type,
                        'current_sentiment': current_sentiment,
                        'current_confidence': current_confidence,
                        'other_analyses': other_analyses,
                        'comment': f"Maintaining {current_sentiment} sentiment with {current_confidence:.2f} confidence"
                    }
                    discussion_history.append(discussion_entry)
                    
                    # For now, keep the original assessment
                    # In a more sophisticated implementation, agents could revise based on discussion
                    new_outputs.append(agent)
                    new_confidence_scores.append(current_confidence)
                else:
                    # Consensus reached or max rounds reached
                    new_outputs.append(agent)
                    new_confidence_scores.append(current_confidence)
            
            return EnhancedAnalysisState(
                review=state.review,
                agent_outputs=new_outputs,
                consensus=state.consensus,
                discussion_history=discussion_history,
                round=state.round + 1,
                product_category=state.product_category,
                confidence_scores=new_confidence_scores
            )
        
        def consensus_step(state: EnhancedAnalysisState):
            """Consensus step - build final consensus from all agent outputs"""
            print(f"\n[EnhancedCoordinator] Building consensus...")
            
            try:
                # Use the new coordinator prompts
                consensus_prompt = CoordinatorPrompts.get_consensus_prompt(state.agent_outputs)
                consensus_chain = ChatPromptTemplate.from_messages([
                    ("system", consensus_prompt),
                    ("human", "Please provide the consensus analysis in JSON format.")
                ]) | self.consensus_llm
                consensus_result = consensus_chain.invoke({})
                # If the result is an AIMessage, extract .content
                if hasattr(consensus_result, 'content'):
                    consensus_result = consensus_result.content
                # Parse the consensus result
                if isinstance(consensus_result, str):
                    import re
                    import json
                    json_match = re.search(r'\{.*\}', consensus_result, re.DOTALL)
                    if json_match:
                        consensus_result = json.loads(json_match.group())
                    else:
                        consensus_result = {
                            "overall_sentiment": "neutral",
                            "overall_confidence": 0.5,
                            "agreement_level": "low",
                            "key_insights": "Consensus analysis failed",
                            "areas_of_disagreement": "Unable to assess",
                            "final_reasoning": consensus_result,
                            "business_recommendations": "Manual review recommended"
                        }
                print(f"[EnhancedCoordinator] Consensus: {consensus_result.get('overall_sentiment', 'unknown')} "
                      f"(confidence: {consensus_result.get('overall_confidence', 0.5):.2f})")
            except Exception as e:
                print(f"[EnhancedCoordinator] Consensus error: {e}")
                consensus_result = {
                    "overall_sentiment": "neutral",
                    "overall_confidence": 0.5,
                    "agreement_level": "low",
                    "key_insights": f"Consensus analysis failed: {str(e)}",
                    "areas_of_disagreement": "Unable to assess due to errors",
                    "final_reasoning": "System encountered technical difficulties",
                    "business_recommendations": "Manual review recommended"
                }
            
            return EnhancedAnalysisState(
                review=state.review,
                agent_outputs=state.agent_outputs,
                consensus=consensus_result,
                discussion_history=state.discussion_history,
                round=state.round,
                product_category=state.product_category,
                confidence_scores=state.confidence_scores
            )
        
        def should_continue_discussion(state: EnhancedAnalysisState):
            """Determine if discussion should continue"""
            if state.round >= self.max_rounds:
                return "consensus_step"
            
            # Check if agents agree
            sentiments = [o['sentiment'] for o in state.agent_outputs]
            if len(set(sentiments)) == 1:
                return "consensus_step"
            
            return "discussion"
        
        # Add nodes to the graph
        g.add_node("analyze", analyze_step)
        g.add_node("discussion", discussion_step)
        g.add_node("consensus_step", consensus_step)
        
        # Set entry point
        g.set_entry_point("analyze")
        
        # Add edges
        g.add_edge("analyze", "discussion")
        g.add_conditional_edges(
            "discussion",
            should_continue_discussion,
            {
                "discussion": "discussion",
                "consensus_step": "consensus_step"
            }
        )
        g.add_edge("consensus_step", END)
        
        return g.compile()

    def run_workflow(self, 
                    product_id: Optional[str] = None, 
                    reviews: Optional[List[str]] = None,
                    product_category: Optional[str] = None) -> Dict[str, Any]:
        """Run the enhanced multi-agent workflow"""
        
        if product_category:
            self.change_product_category(product_category)
        
        # Prepare review data
        if reviews:
            # Use provided reviews
            review_data = {
                'text': reviews[0] if isinstance(reviews, list) else str(reviews),
                'cleaned_text': reviews[0] if isinstance(reviews, list) else str(reviews),
                'product_id': product_id or 'unknown'
            }
        else:
            # Scrape reviews if not provided
            if product_id:
                scraped_reviews = self.scraper.scrape_reviews(product_id)
                if scraped_reviews:
                    review_data = {
                        'text': scraped_reviews[0],
                        'cleaned_text': self.preprocessor.preprocess(scraped_reviews[0]),
                        'product_id': product_id
                    }
                else:
                    raise ValueError(f"No reviews found for product ID: {product_id}")
            else:
                raise ValueError("Either product_id or reviews must be provided")
        
        # Run the workflow
        try:
            final_state = self.graph.invoke({
                'review': review_data,
                'product_category': self.product_category
            })
            
            # Prepare final result
            result = {
                'product_id': review_data['product_id'],
                'product_category': self.product_category,
                'review_text': review_data['cleaned_text'],
                'agent_analyses': final_state['agent_outputs'],
                'consensus': final_state['consensus'],
                'discussion_history': final_state['discussion_history'],
                'analysis_metadata': {
                    'total_agents': len(self.sentiment_agents),
                    'discussion_rounds': final_state['round'],
                    'average_confidence': statistics.mean(final_state['confidence_scores']) if final_state['confidence_scores'] else 0.5,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            }
            
            return result
            
        except Exception as e:
            print(f"[EnhancedCoordinator] Workflow error: {e}")
            return {
                'error': str(e),
                'product_id': product_id,
                'product_category': self.product_category
            }

    def get_available_categories(self) -> List[str]:
        """Get available product categories"""
        return ProductPrompts.get_available_categories()

    def change_product_category(self, new_category: str):
        """Change the product category and recreate agents with new prompts"""
        if new_category not in self.get_available_categories():
            raise ValueError(f"Unknown product category: {new_category}. Available: {self.get_available_categories()}")
        
        self.product_category = new_category
        
        # Recreate agents with new product category
        agent_types = [agent.agent_type for agent in self.sentiment_agents]
        self.sentiment_agents = SentimentAgentFactory.create_agent_team(
            config=self.config,
            agent_types=agent_types,
            max_tokens=self.max_tokens_per_agent,
            product_category=new_category
        )
        
        print(f"[EnhancedCoordinator] Changed to {new_category} category and recreated agents") 