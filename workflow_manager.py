# workflow_manager.py
"""
Simple 3-Layer Multi-Agent Sentiment Analysis Workflow Manager

This replaces the complex enhanced_coordinator with a straightforward pipeline:
Layer 1: Department Agents (Quality, Experience, UX, Business, Technical)
Layer 2: Master Sentiment Analyst (Synthesizes department inputs)
Layer 3: Business Advisor (Provides actionable recommendations)
"""

import json
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from agents.sentiment_agents import SentimentAgentFactory

class MultiAgentWorkflowManager:
    """Simple 3-layer workflow manager for multi-agent sentiment analysis"""
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 product_category: str = "electronics",
                 department_types: Optional[List[str]] = None,
                 max_tokens_per_department: int = 150,
                 max_tokens_master: int = 500,
                 max_tokens_advisor: int = 600):
        
        # Load config
        if config is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        self.config = config
        self.product_category = product_category
        self.max_tokens_per_department = max_tokens_per_department
        self.max_tokens_master = max_tokens_master
        self.max_tokens_advisor = max_tokens_advisor
        
        # Default department types
        if department_types is None:
            department_types = ["quality", "experience", "user_experience", "business", "technical"]
        
        self.department_types = department_types
        
        # Initialize agents
        print(f"[WorkflowManager] Initializing {len(department_types)} department agents...")
        self.department_agents = []
        for dept_type in department_types:
            agent = SentimentAgentFactory.create_agent(
                dept_type, config, max_tokens_per_department, product_category
            )
            self.department_agents.append(agent)
            print(f"[WorkflowManager]   ✓ {dept_type} department ready")
        
        # Initialize Master Analyst
        print(f"[WorkflowManager] Initializing Master Sentiment Analyst...")
        self.master_analyst = SentimentAgentFactory.create_agent(
            "master_analyst", config, max_tokens_master, product_category
        )
        print(f"[WorkflowManager]   ✓ Master Analyst ready")
        
        # Initialize Business Advisor  
        print(f"[WorkflowManager] Initializing Business Advisor...")
        self.business_advisor = SentimentAgentFactory.create_agent(
            "business_advisor", config, max_tokens_advisor, product_category
        )
        print(f"[WorkflowManager]   ✓ Business Advisor ready")
        
        print(f"[WorkflowManager] 3-layer workflow ready for {product_category} products!")
    
    def run_analysis(self, review: str, product_id: str = "unknown") -> Dict[str, Any]:
        """Run the complete 3-layer analysis workflow"""
        
        start_time = time.time()
        
        print(f"\n[WorkflowManager] Starting 3-layer analysis...")
        print(f"[WorkflowManager] Review: {review[:100]}...")
        
        try:
            # LAYER 1: Department Analysis
            print(f"\n[WorkflowManager] LAYER 1: Running department analysis...")
            department_results = self._run_department_analysis(review)
            
            # LAYER 2: Master Analyst Synthesis
            print(f"\n[WorkflowManager] LAYER 2: Master Analyst synthesis...")
            master_analysis = self._run_master_analysis(department_results, review)
            
            # LAYER 3: Business Advisor Recommendations
            print(f"\n[WorkflowManager] LAYER 3: Business Advisor recommendations...")
            business_recommendations = self._run_business_advisor(master_analysis, department_results, review)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Compile final result
            result = {
                'product_id': product_id,
                'product_category': self.product_category,
                'review_text': review,
                'department_analyses': department_results,
                'master_analysis': master_analysis,
                'business_recommendations': business_recommendations,
                'workflow_metadata': {
                    'total_departments': len(self.department_agents),
                    'processing_time': processing_time,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'workflow_version': '3-layer-v1.0'
                }
            }
            
            print(f"\n[WorkflowManager] ✅ Analysis complete in {processing_time:.2f}s")
            print(f"[WorkflowManager] Final sentiment: {master_analysis.get('sentiment', 'unknown')}")
            print(f"[WorkflowManager] Recommendation confidence: {business_recommendations.get('confidence', 0.5):.2f}")
            
            return result
            
        except Exception as e:
            print(f"[WorkflowManager] ❌ Workflow error: {e}")
            return {
                'error': str(e),
                'product_id': product_id,
                'product_category': self.product_category,
                'review_text': review,
                'workflow_metadata': {
                    'processing_time': time.time() - start_time,
                    'error_timestamp': datetime.now().isoformat()
                }
            }
    
    def _run_department_analysis(self, review: str) -> List[Dict[str, Any]]:
        """Layer 1: Run all department agents"""
        
        department_results = []
        
        for i, agent in enumerate(self.department_agents):
            dept_type = self.department_types[i]
            print(f"[WorkflowManager]   Running {dept_type} department...")
            
            try:
                result = agent.analyze(review)
                department_results.append(result)
                sentiment = result.get('sentiment', 'unknown')
                confidence = result.get('confidence', 0.5)
                print(f"[WorkflowManager]   ✓ {dept_type}: {sentiment} ({confidence:.2f})")
                
            except Exception as e:
                print(f"[WorkflowManager]   ❌ {dept_type} error: {e}")
                # Add error result
                department_results.append({
                    'agent_type': dept_type,
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'emotions': [],
                    'topics': [],
                    'reasoning': f"Department analysis error: {str(e)}",
                    'business_impact': "Unable to assess",
                    'error': str(e)
                })
        
        return department_results
    
    def _run_master_analysis(self, department_results: List[Dict[str, Any]], review: str) -> Dict[str, Any]:
        """Layer 2: Master Analyst synthesis"""
        
        try:
            master_result = self.master_analyst.synthesize_department_analyses(department_results, review)
            sentiment = master_result.get('sentiment', 'unknown')
            confidence = master_result.get('confidence', 0.5)
            print(f"[WorkflowManager]   ✓ Master synthesis: {sentiment} ({confidence:.2f})")
            return master_result
            
        except Exception as e:
            print(f"[WorkflowManager]   ❌ Master analysis error: {e}")
            return {
                'agent_type': 'master_analyst',
                'sentiment': 'neutral',
                'confidence': 0.5,
                'emotions': [],
                'topics': [],
                'reasoning': f"Master analysis error: {str(e)}",
                'business_impact': "Unable to synthesize",
                'department_inputs': department_results,
                'error': str(e)
            }
    
    def _run_business_advisor(self, master_analysis: Dict[str, Any], department_results: List[Dict[str, Any]], review: str) -> Dict[str, Any]:
        """Layer 3: Business Advisor recommendations"""
        
        try:
            advisor_result = self.business_advisor.provide_recommendations(master_analysis, department_results, review)
            confidence = advisor_result.get('confidence', 0.5)
            print(f"[WorkflowManager]   ✓ Business recommendations ready ({confidence:.2f})")
            return advisor_result
            
        except Exception as e:
            print(f"[WorkflowManager]   ❌ Business advisor error: {e}")
            return {
                'agent_type': 'business_advisor',
                'sentiment': master_analysis.get('sentiment', 'neutral'),
                'confidence': 0.5,
                'emotions': [],
                'topics': [],
                'reasoning': f"Business advisor error: {str(e)}",
                'business_impact': "Unable to provide recommendations",
                'master_analysis': master_analysis,
                'department_analyses': department_results,
                'error': str(e)
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the current workflow configuration"""
        
        return {
            'product_category': self.product_category,
            'department_types': self.department_types,
            'total_agents': len(self.department_agents) + 2,  # +2 for master and advisor
            'max_tokens_per_department': self.max_tokens_per_department,
            'max_tokens_master': self.max_tokens_master,
            'max_tokens_advisor': self.max_tokens_advisor,
            'workflow_version': '3-layer-v1.0'
        }
    
    def change_product_category(self, new_category: str):
        """Change product category and reinitialize agents"""
        
        print(f"[WorkflowManager] Changing from {self.product_category} to {new_category}...")
        self.product_category = new_category
        
        # Reinitialize all agents with new category
        self.department_agents = []
        for dept_type in self.department_types:
            agent = SentimentAgentFactory.create_agent(
                dept_type, self.config, self.max_tokens_per_department, new_category
            )
            self.department_agents.append(agent)
        
        self.master_analyst = SentimentAgentFactory.create_agent(
            "master_analyst", self.config, self.max_tokens_master, new_category
        )
        
        self.business_advisor = SentimentAgentFactory.create_agent(
            "business_advisor", self.config, self.max_tokens_advisor, new_category
        )
        
        print(f"[WorkflowManager] ✅ Successfully changed to {new_category}")


# Convenience function for easy usage
def analyze_review(review: str, 
                  product_category: str = "electronics",
                  config: Optional[Dict[str, Any]] = None,
                  department_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze a single review using the 3-layer workflow
    
    Args:
        review: Review text to analyze
        product_category: Product category for specialized analysis
        config: Optional config dict, will load from config.json if None
        department_types: List of department types, defaults to all 5 departments
    
    Returns:
        Complete analysis result with department, master, and business advisor insights
    """
    
    workflow = MultiAgentWorkflowManager(
        config=config,
        product_category=product_category,
        department_types=department_types
    )
    
    return workflow.run_analysis(review) 