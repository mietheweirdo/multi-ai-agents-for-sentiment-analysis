# agents/langgraph_coordinator.py
"""
LangGraph Multi-Agent Sentiment Analysis Coordinator
Implements agent-to-agent communication, discussion rounds, and consensus building
"""

import json
import os
import time
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from datetime import datetime

# LangGraph imports
from langgraph.graph import StateGraph, END, add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agents.sentiment_agents import SentimentAgentFactory

class AgentState(TypedDict):
    """State shared between all agents in the workflow"""
    review: str
    product_category: str
    product_id: str
    
    # Agent analyses
    department_analyses: List[Dict[str, Any]]
    discussion_messages: Annotated[List, add_messages]
    consensus_reached: bool
    disagreement_level: float
    
    # Final results
    master_analysis: Dict[str, Any]
    business_recommendations: Dict[str, Any]
    
    # Workflow metadata
    workflow_metadata: Dict[str, Any]
    current_round: int
    max_discussion_rounds: int

class LangGraphCoordinator:
    """LangGraph-based multi-agent coordinator with discussion capabilities"""
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 product_category: str = "electronics",
                 department_types: Optional[List[str]] = None,
                 max_tokens_per_department: int = 150,
                 max_tokens_master: int = 500,
                 max_tokens_advisor: int = 600,
                 max_discussion_rounds: int = 2,
                 disagreement_threshold: float = 0.6):
        
        # Load config
        if config is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        self.config = config
        self.product_category = product_category
        self.max_tokens_per_department = max_tokens_per_department
        self.max_tokens_master = max_tokens_master
        self.max_tokens_advisor = max_tokens_advisor
        self.max_discussion_rounds = max_discussion_rounds
        self.disagreement_threshold = disagreement_threshold
        
        # Default department types
        if department_types is None:
            department_types = ["quality", "experience", "user_experience", "business", "technical"]
        
        self.department_types = department_types
        
        # Initialize agents
        print(f"[LangGraphCoordinator] Initializing {len(department_types)} department agents...")
        self.department_agents = {}
        for dept_type in department_types:
            agent = SentimentAgentFactory.create_agent(
                dept_type, config, max_tokens_per_department, product_category
            )
            self.department_agents[dept_type] = agent
            print(f"[LangGraphCoordinator]   ✓ {dept_type} department ready")
        
        # Initialize Master Analyst
        self.master_analyst = SentimentAgentFactory.create_agent(
            "master_analyst", config, max_tokens_master, product_category
        )
        
        # Initialize Business Advisor  
        self.business_advisor = SentimentAgentFactory.create_agent(
            "business_advisor", config, max_tokens_advisor, product_category
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        print(f"[LangGraphCoordinator] LangGraph workflow ready for {product_category} products!")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with agent nodes and edges"""
        
        workflow = StateGraph(AgentState)
        
        # Add department agent nodes
        for dept_type in self.department_types:
            workflow.add_node(f"{dept_type}_analysis", self._create_department_node(dept_type))
        
        # Add discussion and consensus nodes
        workflow.add_node("check_consensus", self._check_consensus_node)
        workflow.add_node("agent_discussion", self._agent_discussion_node)
        workflow.add_node("master_synthesis", self._master_synthesis_node)
        workflow.add_node("business_advisor", self._business_recommendations_node)
        
        # Add edges - start with parallel department analysis
        workflow.set_entry_point("quality_analysis")
        
        # Department agents run in sequence (could be parallel but for cost control)
        for i, dept_type in enumerate(self.department_types):
            if i < len(self.department_types) - 1:
                next_dept = self.department_types[i + 1]
                workflow.add_edge(f"{dept_type}_analysis", f"{next_dept}_analysis")
            else:
                # Last department agent goes to consensus check
                workflow.add_edge(f"{dept_type}_analysis", "check_consensus")
        
        # Consensus check decides next step
        workflow.add_conditional_edges(
            "check_consensus",
            self._should_discuss,
            {
                "discuss": "agent_discussion",
                "synthesize": "master_synthesis"
            }
        )
        
        # After discussion, check consensus again
        workflow.add_edge("agent_discussion", "check_consensus")
        
        # Final steps
        workflow.add_edge("master_synthesis", "business_advisor")
        workflow.add_edge("business_advisor", END)
        
        return workflow.compile()
    
    def _create_department_node(self, dept_type: str):
        """Create a node function for a specific department agent"""
        
        def department_node(state: AgentState) -> AgentState:
            print(f"[LangGraphCoordinator] Running {dept_type} analysis...")
            
            try:
                agent = self.department_agents[dept_type]
                
                # Include previous analyses in context if available
                context = state["review"]
                if state.get("department_analyses"):
                    context += "\n\nPREVIOUS AGENT ANALYSES:\n"
                    for analysis in state["department_analyses"]:
                        context += f"- {analysis['agent_type']}: {analysis['sentiment']} ({analysis['reasoning'][:100]}...)\n"
                
                result = agent.analyze(context)
                
                # Add to department analyses
                new_analyses = state.get("department_analyses", [])
                new_analyses.append(result)
                
                sentiment = result.get('sentiment', 'unknown')
                confidence = result.get('confidence', 0.5)
                print(f"[LangGraphCoordinator]   ✓ {dept_type}: {sentiment} ({confidence:.2f})")
                
                return {
                    **state,
                    "department_analyses": new_analyses
                }
                
            except Exception as e:
                print(f"[LangGraphCoordinator]   ❌ {dept_type} error: {e}")
                
                error_result = {
                    'agent_type': dept_type,
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'emotions': [],
                    'topics': [],
                    'reasoning': f"Department analysis error: {str(e)}",
                    'business_impact': "Unable to assess",
                    'error': str(e)
                }
                
                new_analyses = state.get("department_analyses", [])
                new_analyses.append(error_result)
                
                return {
                    **state,
                    "department_analyses": new_analyses
                }
        
        return department_node
    
    def _check_consensus_node(self, state: AgentState) -> AgentState:
        """Check if agents have reached consensus or if discussion is needed"""
        
        analyses = state.get("department_analyses", [])
        if len(analyses) < 2:
            return {
                **state,
                "consensus_reached": True,
                "disagreement_level": 0.0
            }
        
        # Calculate disagreement level
        sentiments = [a.get('sentiment', 'neutral') for a in analyses]
        sentiment_counts = {}
        for sentiment in sentiments:
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Calculate disagreement as 1 - (most_common_sentiment_ratio)
        max_count = max(sentiment_counts.values())
        agreement_ratio = max_count / len(sentiments)
        disagreement_level = 1.0 - agreement_ratio
        
        consensus_reached = disagreement_level < self.disagreement_threshold
        
        print(f"[LangGraphCoordinator] Consensus check: disagreement={disagreement_level:.2f}, threshold={self.disagreement_threshold}")
        print(f"[LangGraphCoordinator] Consensus reached: {consensus_reached}")
        
        return {
            **state,
            "consensus_reached": consensus_reached,
            "disagreement_level": disagreement_level
        }
    
    def _should_discuss(self, state: AgentState) -> str:
        """Conditional edge function to decide if discussion is needed"""
        
        if state.get("consensus_reached", True):
            return "synthesize"
        
        current_round = state.get("current_round", 0)
        max_rounds = state.get("max_discussion_rounds", self.max_discussion_rounds)
        
        if current_round >= max_rounds:
            print(f"[LangGraphCoordinator] Max discussion rounds reached, proceeding to synthesis")
            return "synthesize"
        
        return "discuss"
    
    def _agent_discussion_node(self, state: AgentState) -> AgentState:
        """Facilitate discussion between agents to resolve disagreements"""
        
        print(f"[LangGraphCoordinator] Starting agent discussion round {state.get('current_round', 0) + 1}...")
        
        analyses = state.get("department_analyses", [])
        discussion_messages = state.get("discussion_messages", [])
        
        # Create discussion context
        discussion_context = f"""
REVIEW: {state['review']}

CURRENT AGENT ANALYSES:
"""
        
        for analysis in analyses:
            agent_type = analysis.get('agent_type', 'unknown')
            sentiment = analysis.get('sentiment', 'neutral')
            confidence = analysis.get('confidence', 0.5)
            reasoning = analysis.get('reasoning', '')
            
            discussion_context += f"""
{agent_type.upper()} AGENT:
- Sentiment: {sentiment} (confidence: {confidence:.2f})
- Reasoning: {reasoning}
"""
        
        discussion_context += f"""
DISAGREEMENT LEVEL: {state.get('disagreement_level', 0.0):.2f}

Please discuss and refine your analyses considering other agents' perspectives.
Each agent should provide a refined analysis considering the discussion.
"""
        
        # Get refined analyses from each agent
        refined_analyses = []
        new_messages = []
        
        for dept_type in self.department_types:
            try:
                agent = self.department_agents[dept_type]
                
                # Create agent-specific discussion prompt
                agent_prompt = f"""
You are the {dept_type.upper()} specialist. 

{discussion_context}

Based on the discussion above, provide your REFINED analysis of the review.
Consider other agents' perspectives but maintain your specialized focus on {dept_type}.
Be willing to adjust your sentiment if other agents make valid points.
"""
                
                refined_result = agent.analyze(agent_prompt)
                refined_analyses.append(refined_result)
                
                # Add to discussion messages
                message = f"{dept_type.upper()}: {refined_result.get('sentiment')} - {refined_result.get('reasoning', '')[:100]}..."
                new_messages.append(HumanMessage(content=message))
                
                print(f"[LangGraphCoordinator]   🗣️ {dept_type} refined: {refined_result.get('sentiment')}")
                
            except Exception as e:
                print(f"[LangGraphCoordinator]   ❌ {dept_type} discussion error: {e}")
                # Keep original analysis if discussion fails
                original = next((a for a in analyses if a.get('agent_type') == dept_type), None)
                if original:
                    refined_analyses.append(original)
        
        return {
            **state,
            "department_analyses": refined_analyses,
            "discussion_messages": discussion_messages + new_messages,
            "current_round": state.get("current_round", 0) + 1
        }
    
    def _master_synthesis_node(self, state: AgentState) -> AgentState:
        """Master analyst synthesizes all department analyses"""
        
        print(f"[LangGraphCoordinator] Master analyst synthesis...")
        
        try:
            department_results = state.get("department_analyses", [])
            review = state["review"]
            
            master_result = self.master_analyst.synthesize_department_analyses(department_results, review)
            
            sentiment = master_result.get('sentiment', 'unknown')
            confidence = master_result.get('confidence', 0.5)
            print(f"[LangGraphCoordinator]   ✓ Master synthesis: {sentiment} ({confidence:.2f})")
            
            return {
                **state,
                "master_analysis": master_result
            }
            
        except Exception as e:
            print(f"[LangGraphCoordinator]   ❌ Master analysis error: {e}")
            
            error_result = {
                'agent_type': 'master_analyst',
                'sentiment': 'neutral',
                'confidence': 0.5,
                'emotions': [],
                'topics': [],
                'reasoning': f"Master analysis error: {str(e)}",
                'business_impact': "Unable to synthesize",
                'department_inputs': state.get("department_analyses", []),
                'error': str(e)
            }
            
            return {
                **state,
                "master_analysis": error_result
            }
    
    def _business_recommendations_node(self, state: AgentState) -> AgentState:
        """Business advisor provides final recommendations"""
        
        print(f"[LangGraphCoordinator] Business advisor recommendations...")
        
        try:
            master_analysis = state.get("master_analysis", {})
            department_results = state.get("department_analyses", [])
            review = state["review"]
            
            advisor_result = self.business_advisor.provide_recommendations(
                master_analysis, department_results, review
            )
            
            confidence = advisor_result.get('confidence', 0.5)
            print(f"[LangGraphCoordinator]   ✓ Business recommendations ready ({confidence:.2f})")
            
            # Update workflow metadata
            workflow_metadata = {
                'total_departments': len(self.department_types),
                'discussion_rounds': state.get("current_round", 0),
                'disagreement_level': state.get("disagreement_level", 0.0),
                'consensus_reached': state.get("consensus_reached", True),
                'analysis_timestamp': datetime.now().isoformat(),
                'workflow_version': 'langgraph-v1.0'
            }
            
            return {
                **state,
                "business_recommendations": advisor_result,
                "workflow_metadata": workflow_metadata
            }
            
        except Exception as e:
            print(f"[LangGraphCoordinator]   ❌ Business advisor error: {e}")
            
            error_result = {
                'agent_type': 'business_advisor',
                'sentiment': state.get("master_analysis", {}).get('sentiment', 'neutral'),
                'confidence': 0.5,
                'emotions': [],
                'topics': [],
                'reasoning': f"Business advisor error: {str(e)}",
                'business_impact': "Unable to provide recommendations",
                'master_analysis': state.get("master_analysis", {}),
                'department_analyses': state.get("department_analyses", []),
                'error': str(e)
            }
            
            workflow_metadata = {
                'total_departments': len(self.department_types),
                'discussion_rounds': state.get("current_round", 0),
                'disagreement_level': state.get("disagreement_level", 0.0),
                'consensus_reached': state.get("consensus_reached", True),
                'analysis_timestamp': datetime.now().isoformat(),
                'workflow_version': 'langgraph-v1.0',
                'error': str(e)
            }
            
            return {
                **state,
                "business_recommendations": error_result,
                "workflow_metadata": workflow_metadata
            }
    
    def run_analysis(self, review: str, product_id: str = "unknown") -> Dict[str, Any]:
        """Run the complete LangGraph multi-agent analysis workflow"""
        
        start_time = time.time()
        
        print(f"\n[LangGraphCoordinator] Starting LangGraph multi-agent analysis...")
        print(f"[LangGraphCoordinator] Review: {review[:100]}...")
        
        try:
            # Initialize state
            initial_state = AgentState(
                review=review,
                product_category=self.product_category,
                product_id=product_id,
                department_analyses=[],
                discussion_messages=[],
                consensus_reached=False,
                disagreement_level=0.0,
                master_analysis={},
                business_recommendations={},
                workflow_metadata={},
                current_round=0,
                max_discussion_rounds=self.max_discussion_rounds
            )
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Update processing time in metadata
            final_state["workflow_metadata"]["processing_time"] = processing_time
            
            # Compile final result
            result = {
                'product_id': product_id,
                'product_category': self.product_category,
                'review_text': review,
                'department_analyses': final_state.get("department_analyses", []),
                'discussion_messages': [msg.content for msg in final_state.get("discussion_messages", [])],
                'master_analysis': final_state.get("master_analysis", {}),
                'business_recommendations': final_state.get("business_recommendations", {}),
                'workflow_metadata': final_state.get("workflow_metadata", {})
            }
            
            print(f"\n[LangGraphCoordinator] ✅ LangGraph analysis complete in {processing_time:.2f}s")
            print(f"[LangGraphCoordinator] Discussion rounds: {final_state.get('current_round', 0)}")
            print(f"[LangGraphCoordinator] Final sentiment: {final_state.get('master_analysis', {}).get('sentiment', 'unknown')}")
            print(f"[LangGraphCoordinator] Consensus reached: {final_state.get('consensus_reached', True)}")
            
            return result
            
        except Exception as e:
            print(f"[LangGraphCoordinator] ❌ LangGraph workflow error: {e}")
            return {
                'error': str(e),
                'product_id': product_id,
                'product_category': self.product_category,
                'review_text': review,
                'workflow_metadata': {
                    'processing_time': time.time() - start_time,
                    'error_timestamp': datetime.now().isoformat(),
                    'workflow_version': 'langgraph-v1.0'
                }
            }
    
    def change_product_category(self, new_category: str):
        """Change product category and reinitialize agents and workflow"""
        
        print(f"[LangGraphCoordinator] Changing from {self.product_category} to {new_category}...")
        self.product_category = new_category
        
        # Reinitialize all agents with new category
        self.department_agents = {}
        for dept_type in self.department_types:
            agent = SentimentAgentFactory.create_agent(
                dept_type, self.config, self.max_tokens_per_department, new_category
            )
            self.department_agents[dept_type] = agent
        
        self.master_analyst = SentimentAgentFactory.create_agent(
            "master_analyst", self.config, self.max_tokens_master, new_category
        )
        
        self.business_advisor = SentimentAgentFactory.create_agent(
            "business_advisor", self.config, self.max_tokens_advisor, new_category
        )
        
        # Rebuild workflow with new agents
        self.workflow = self._build_workflow()
        
        print(f"[LangGraphCoordinator] ✅ Successfully changed to {new_category}")


# Convenience function for easy usage
def analyze_with_langgraph(review: str, 
                          product_category: str = "electronics",
                          config: Optional[Dict[str, Any]] = None,
                          department_types: Optional[List[str]] = None,
                          max_discussion_rounds: int = 2,
                          disagreement_threshold: float = 0.6) -> Dict[str, Any]:
    """
    Convenience function to analyze a review using LangGraph multi-agent workflow
    
    Args:
        review: Review text to analyze
        product_category: Product category for specialized analysis
        config: Optional config dict, will load from config.json if None
        department_types: List of department types, defaults to all 5 departments
        max_discussion_rounds: Maximum number of discussion rounds between agents
        disagreement_threshold: Threshold for triggering agent discussion (0.0-1.0)
    
    Returns:
        Complete analysis result with agent discussion logs and consensus info
    """
    
    coordinator = LangGraphCoordinator(
        config=config,
        product_category=product_category,
        department_types=department_types,
        max_discussion_rounds=max_discussion_rounds,
        disagreement_threshold=disagreement_threshold
    )
    
    return coordinator.run_analysis(review) 