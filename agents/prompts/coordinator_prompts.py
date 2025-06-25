"""
Coordinator-specific prompts for consensus building and discussion phases.
These prompts help agents collaborate and reach agreement on sentiment analysis.
"""

from typing import Dict, List, Any

class CoordinatorPrompts:
    """Prompts for coordinator and consensus building"""
    
    # Consensus building prompt
    CONSENSUS_PROMPT = """You are a Consensus Coordinator for a multi-agent sentiment analysis system.

Your task is to analyze the outputs from multiple specialized agents and reach a consensus on the overall sentiment.

AGENT ANALYSES:
{agent_analyses}

CONSENSUS REQUIREMENTS:
- Consider all agent perspectives equally
- Weight confidence scores appropriately
- Identify areas of agreement and disagreement
- Provide reasoning for final consensus
- Consider business impact across all dimensions

Please provide a consensus analysis with:
- overall_sentiment: positive/neutral/negative
- overall_confidence: weighted confidence score (0.0-1.0)
- agreement_level: high/medium/low based on agent agreement
- key_insights: main findings from all agents
- areas_of_disagreement: any conflicting assessments
- final_reasoning: consensus reasoning (max 150 words)
- business_recommendations: actionable business insights (max 100 words)"""

    # Discussion phase prompt
    DISCUSSION_PROMPT = """You are participating in a multi-agent discussion to reach consensus on sentiment analysis.

CURRENT ROUND: {round_number}
YOUR ROLE: {agent_role}
YOUR CURRENT ASSESSMENT: {current_assessment}

OTHER AGENTS' PERSPECTIVES:
{other_analyses}

DISCUSSION GUIDELINES:
- Consider other agents' perspectives respectfully
- Provide evidence for your position
- Be open to revising your assessment if convinced
- Focus on the most important aspects for your specialization
- Keep responses concise and constructive

Please provide your updated assessment with:
- revised_sentiment: your updated sentiment assessment
- revised_confidence: your updated confidence level
- reasoning: why you maintain or change your position
- key_evidence: supporting evidence for your position
- collaboration_notes: how you considered other perspectives"""

    # Final summary prompt
    SUMMARY_PROMPT = """You are creating a final summary report for a multi-agent sentiment analysis.

ANALYSIS RESULTS:
{consensus_results}

AGENT CONTRIBUTIONS:
{agent_contributions}

PRODUCT CONTEXT:
- Category: {product_category}
- Review Count: {review_count}
- Analysis Date: {analysis_date}

Please create a comprehensive summary report with:
- executive_summary: high-level findings (max 100 words)
- sentiment_overview: overall sentiment with confidence
- key_findings: main insights from each agent type
- business_impact: strategic business implications
- recommendations: actionable next steps
- risk_assessment: potential risks or concerns
- opportunities: growth or improvement opportunities"""

    # Error handling prompt
    ERROR_HANDLING_PROMPT = """Error in multi-agent analysis: {error_message}

Please provide a fallback consensus with:
- overall_sentiment: neutral
- overall_confidence: 0.5
- agreement_level: low
- key_insights: "Analysis incomplete due to technical issues"
- areas_of_disagreement: "Unable to assess due to errors"
- final_reasoning: "System encountered technical difficulties"
- business_recommendations: "Manual review recommended" """

    @staticmethod
    def format_agent_analyses(agent_outputs: List[Dict[str, Any]]) -> str:
        """Format agent analyses for consensus prompt"""
        formatted = []
        for i, output in enumerate(agent_outputs, 1):
            agent_type = output.get('agent_type', f'Agent {i}')
            sentiment = output.get('sentiment', 'neutral')
            confidence = output.get('confidence', 0.5)
            reasoning = output.get('reasoning', 'No reasoning provided')
            
            formatted.append(f"""
AGENT {i} ({agent_type.upper()}):
- Sentiment: {sentiment}
- Confidence: {confidence:.2f}
- Reasoning: {reasoning}
""")
        
        return '\n'.join(formatted)

    @staticmethod
    def format_other_analyses(agent_outputs: List[Dict[str, Any]], current_agent_index: int) -> str:
        """Format other agents' analyses for discussion prompt"""
        formatted = []
        for i, output in enumerate(agent_outputs):
            if i == current_agent_index:
                continue
                
            agent_type = output.get('agent_type', f'Agent {i+1}')
            sentiment = output.get('sentiment', 'neutral')
            confidence = output.get('confidence', 0.5)
            reasoning = output.get('reasoning', 'No reasoning provided')
            
            formatted.append(f"""
{agent_type.upper()}:
- Sentiment: {sentiment}
- Confidence: {confidence:.2f}
- Reasoning: {reasoning}
""")
        
        return '\n'.join(formatted)

    @staticmethod
    def format_agent_contributions(agent_outputs: List[Dict[str, Any]]) -> str:
        """Format agent contributions for summary prompt"""
        formatted = []
        for output in agent_outputs:
            agent_type = output.get('agent_type', 'Unknown')
            sentiment = output.get('sentiment', 'neutral')
            confidence = output.get('confidence', 0.5)
            business_impact = output.get('business_impact', 'No impact assessed')
            
            formatted.append(f"""
{agent_type.upper()}:
- Sentiment: {sentiment} (confidence: {confidence:.2f})
- Business Impact: {business_impact}
""")
        
        return '\n'.join(formatted)

    @staticmethod
    def get_consensus_prompt(agent_outputs: List[Dict[str, Any]]) -> str:
        """Get formatted consensus prompt"""
        agent_analyses = CoordinatorPrompts.format_agent_analyses(agent_outputs)
        return CoordinatorPrompts.CONSENSUS_PROMPT.format(agent_analyses=agent_analyses)

    @staticmethod
    def get_discussion_prompt(agent_outputs: List[Dict[str, Any]], 
                            current_agent_index: int, 
                            round_number: int,
                            agent_role: str,
                            current_assessment: Dict[str, Any]) -> str:
        """Get formatted discussion prompt"""
        other_analyses = CoordinatorPrompts.format_other_analyses(agent_outputs, current_agent_index)
        current_assessment_str = f"Sentiment: {current_assessment.get('sentiment', 'neutral')}, Confidence: {current_assessment.get('confidence', 0.5):.2f}"
        
        return CoordinatorPrompts.DISCUSSION_PROMPT.format(
            round_number=round_number,
            agent_role=agent_role,
            current_assessment=current_assessment_str,
            other_analyses=other_analyses
        )

    @staticmethod
    def get_summary_prompt(consensus_results: Dict[str, Any],
                          agent_outputs: List[Dict[str, Any]],
                          product_category: str,
                          review_count: int,
                          analysis_date: str) -> str:
        """Get formatted summary prompt"""
        agent_contributions = CoordinatorPrompts.format_agent_contributions(agent_outputs)
        
        return CoordinatorPrompts.SUMMARY_PROMPT.format(
            consensus_results=str(consensus_results),
            agent_contributions=agent_contributions,
            product_category=product_category,
            review_count=review_count,
            analysis_date=analysis_date
        ) 