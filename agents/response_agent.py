# agents/response_agent.py
"""
Response Agent for generating user-friendly chatbot responses
Synthesizes LangGraph analysis results into natural conversational responses
"""

import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ProductResponseAgent:
    """Specialized agent for generating final user responses"""
    
    def __init__(self, config: Dict[str, Any]):
        self.llm = ChatOpenAI(
            model=config.get("model_name", "gpt-4o-mini"),
            api_key=config.get("api_key"),
            max_tokens=400,
            temperature=0.3
        )
        
        # Response generation prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a smart product assistant that provides helpful, natural responses about products.

Your task is to synthesize multi-agent analysis results into a single, readable answer for users.

Guidelines:
- Give direct, helpful answers to user questions
- Use information from the analysis to support your response
- Keep responses conversational and easy to understand
- If it's purchase advice, be balanced and mention key considerations
- If it's about improvements, focus on realistic suggestions
- Always sound confident but not overly promotional
- Don't mention "agents" or "analysis" - just give natural advice

Response should be 2-4 sentences, clear and actionable."""),
            ("human", """{context}

Based on this analysis, provide a natural, helpful response to the user's question: "{user_question}"

Make it sound like you're a knowledgeable friend giving advice, not a technical report.""")
        ])
        
        self.chain = self.prompt | self.llm
    
    def generate_response(self, 
                         analysis_result: Dict[str, Any], 
                         user_input: str, 
                         product_name: str, 
                         question_type: str, 
                         scraped_data: List[Dict]) -> str:
        """Generate final user response from analysis results"""
        
        try:
            # Extract key insights from the analysis
            master_analysis = analysis_result.get("master_analysis", {})
            business_recs = analysis_result.get("business_recommendations", {})
            department_analyses = analysis_result.get("department_analyses", [])
            
            # Build context for response generation
            context = f"USER QUESTION: {user_input}\n"
            context += f"PRODUCT: {product_name}\n"
            context += f"QUESTION TYPE: {question_type}\n"
            context += f"REVIEWS ANALYZED: {len(scraped_data)}\n\n"
            
            # Add master insights
            if master_analysis:
                sentiment = master_analysis.get('sentiment', 'neutral')
                confidence = master_analysis.get('confidence', 0.0)
                reasoning = master_analysis.get('reasoning', '')
                context += f"OVERALL ASSESSMENT: {sentiment} (confidence: {confidence:.2f})\n"
                if reasoning:
                    context += f"KEY INSIGHT: {reasoning}\n\n"
            
            # Add business recommendations
            if business_recs and business_recs.get('business_impact'):
                context += f"BUSINESS PERSPECTIVE: {business_recs['business_impact']}\n\n"
            
            # Add department highlights
            if department_analyses:
                context += "EXPERT INSIGHTS:\n"
                for dept in department_analyses:
                    agent_type = dept.get("agent_type", "unknown")
                    reasoning = dept.get("reasoning", "")
                    if reasoning:
                        context += f"- {agent_type.title()}: {reasoning[:100]}...\n"
            
            # Add review highlights if available
            if scraped_data:
                context += f"\nREVIEW HIGHLIGHTS:\n"
                for i, review in enumerate(scraped_data[:3]):  # Top 3 reviews
                    review_text = review.get('review_text', '')[:150]
                    if review_text:
                        context += f"- Review {i+1}: {review_text}...\n"
            
            # Generate the response
            response = self.chain.invoke({
                "context": context,
                "user_question": user_input
            })
            
            return response.content.strip()
            
        except Exception as e:
            print(f"⚠️ Response generation failed: {e}")
            
            # Intelligent fallback based on question type and product
            if question_type == "purchase_advice":
                return f"Based on current market analysis, {product_name} has both strengths and considerations. I'd recommend evaluating how it fits your specific needs and budget before making a decision."
            
            elif question_type == "improvement_suggestions":
                return f"{product_name} could benefit from enhancements in user experience, performance optimization, and addressing common user feedback. The key areas for improvement seem to be around usability and feature refinement."
            
            elif question_type == "comparison":
                return f"When comparing {product_name} with alternatives, consider factors like your use case, budget, and long-term needs. Each option has its own strengths in different areas."
            
            else:
                return f"Thanks for asking about {product_name}! While I'd love to give you a detailed answer, I recommend checking recent reviews and expert opinions for the most current insights on this product."
