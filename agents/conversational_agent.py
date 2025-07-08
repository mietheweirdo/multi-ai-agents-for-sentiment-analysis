#!/usr/bin/env python3
"""
Conversational Agent with Intent Detection
Handles general chat and triggers product analysis when needed
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationalAgent:
    """
    Intelligent conversational agent that can:
    1. Handle general chat conversations
    2. Detect product improvement queries
    3. Trigger multi-agent analysis for business recommendations
    """
    
    def __init__(self, config: Dict[str, Any], coordinator_endpoint: str = None, use_a2a_coordinator: bool = False):
        self.config = config
        
        # Choose coordinator based on A2A preference
        if use_a2a_coordinator:
            self.coordinator_endpoint = coordinator_endpoint or "http://localhost:8020/rpc"
            self.coordinator_type = "Enhanced A2A Coordinator"
        else:
            self.coordinator_endpoint = coordinator_endpoint or "http://localhost:8000/rpc" 
            self.coordinator_type = "Standard Coordinator"
        
        # Product-related keywords that suggest improvement queries
        self.product_keywords = [
            "improve", "better", "enhance", "fix", "upgrade", "change", 
            "modify", "optimize", "boost", "increase", "develop", "grow",
            "what should i do", "how to make", "recommendations for",
            "suggestions for", "advice for", "help with"
        ]
        
        # Product name patterns (brands, product types)
        self.product_patterns = [
            r'\b(iphone|samsung|oppo|xiaomi|huawei|sony|lg)\s*\w*\b',
            r'\b(macbook|laptop|computer|phone|smartphone|tablet)\b',
            r'\b(dress|shirt|jacket|shoes|bag|watch|headphones)\b',
            r'\b(coffee maker|blender|vacuum|tv|camera|speaker)\b',
            r'\b[a-zA-Z]+\s*\d+\b',  # Brand with numbers like "oppo a93"
        ]
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message and determine response type
        
        Returns:
            dict: {
                'intent': 'general_chat' | 'product_analysis',
                'product_name': str | None,
                'confidence': float,
                'reasoning': str
            }
        """
        message_lower = message.lower()
        
        # Check for product improvement intent
        has_product_keywords = any(keyword in message_lower for keyword in self.product_keywords)
        
        # Extract potential product names
        potential_products = self._extract_product_names(message)
        
        # Determine intent
        if has_product_keywords and potential_products:
            return {
                'intent': 'product_analysis',
                'product_name': potential_products[0],  # Take first match
                'confidence': 0.9,
                'reasoning': f"Detected product improvement query with product '{potential_products[0]}'"
            }
        elif has_product_keywords:
            # Has improvement keywords but no clear product - ask for clarification
            return {
                'intent': 'clarification_needed',
                'product_name': None,
                'confidence': 0.7,
                'reasoning': "Detected improvement intent but no specific product mentioned"
            }
        else:
            return {
                'intent': 'general_chat',
                'product_name': None,
                'confidence': 0.8,
                'reasoning': "General conversation detected"
            }
    
    def _extract_product_names(self, message: str) -> List[str]:
        """Extract potential product names from message"""
        products = []
        
        for pattern in self.product_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            products.extend(matches)
        
        # Also look for quoted products or products after "for"
        quoted_pattern = r'["\']([^"\']+)["\']'
        for_pattern = r'\bfor\s+([a-zA-Z0-9\s]+?)(?:\s|$|[.!?])'
        
        quoted_matches = re.findall(quoted_pattern, message)
        for_matches = re.findall(for_pattern, message, re.IGNORECASE)
        
        products.extend(quoted_matches)
        products.extend([match.strip() for match in for_matches if len(match.strip()) > 2])
        
        # Clean and filter products
        cleaned_products = []
        for product in products:
            if isinstance(product, tuple):
                product = product[0] if product[0] else product[1]
            
            product = product.strip()
            if len(product) > 1 and product.lower() not in ['the', 'and', 'or', 'but', 'it', 'this', 'that']:
                cleaned_products.append(product)
        
        return list(set(cleaned_products))  # Remove duplicates
    
    def handle_general_chat(self, message: str) -> Dict[str, Any]:
        """Handle general conversation using LLM"""
        
        # Enhanced system prompt for general conversation
        system_prompt = """You are a helpful AI assistant specializing in business and product consulting. 
        
        You can help with:
        - General questions about time, date, weather
        - Business advice and strategy
        - Product development discussions
        - Technology and market trends
        - General conversation
        
        If someone asks about improving a specific product, you should mention that you can provide detailed analysis by asking about the specific product they want to improve.
        
        Keep responses conversational, helpful, and concise."""
        
        # Handle some common queries directly
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['time', 'what time', 'current time']):
            current_time = datetime.now().strftime("%I:%M %p")
            return {
                'response': f"The current time is {current_time}.",
                'type': 'direct_response'
            }
        
        if any(word in message_lower for word in ['date', 'today', 'what date']):
            current_date = datetime.now().strftime("%B %d, %Y")
            return {
                'response': f"Today is {current_date}.",
                'type': 'direct_response'
            }
        
        # Use LLM for more complex queries
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.get('api_key'))
            
            response = client.chat.completions.create(
                model=self.config.get('model_name', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return {
                'response': response.choices[0].message.content.strip(),
                'type': 'llm_response'
            }
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {
                'response': "I'm here to help! You can ask me general questions or ask for product improvement recommendations. For example, try asking 'What should I improve for iPhone 14?'",
                'type': 'fallback_response'
            }
    
    def handle_product_analysis(self, product_name: str, original_message: str) -> Dict[str, Any]:
        """
        Trigger product analysis through coordinator and format as human advisor response
        
        Args:
            product_name: Name of the product to analyze
            original_message: Original user message for context
            
        Returns:
            dict: Analysis results or error
        """
        try:
            logger.info(f"Triggering product analysis for: {product_name}")
            
            # Create enhanced analysis request
            analysis_request = f"""
            PRODUCT ANALYSIS REQUEST:
            Product: {product_name}
            User Query: {original_message}
            
            Please perform comprehensive sentiment analysis by:
            1. Auto-scraping reviews from YouTube and Tiki for "{product_name}"
            2. Running multi-agent sentiment analysis
            3. Providing detailed business recommendations for product improvement
            
            Focus on actionable insights that can help improve the product based on customer feedback.
            """
            
            # Prepare RPC payload for coordinator
            payload = {
                "jsonrpc": "2.0",
                "id": f"conv-{datetime.now().timestamp()}",
                "method": "tasks/send",
                "params": {
                    "id": f"analysis-{datetime.now().timestamp()}",
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": analysis_request}]
                    },
                    "metadata": {
                        "product_name": product_name,
                        "original_query": original_message,
                        "analysis_type": "product_improvement",
                        "enable_scraping": True,
                        "sources": ["youtube", "tiki"],
                        "max_items_per_source": 5
                    }
                }
            }
            
            # Call coordinator
            response = requests.post(
                self.coordinator_endpoint,
                json=payload,
                timeout=60  # Longer timeout for scraping + analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "result" in result:
                    # Extract analysis result
                    result_text = result["result"]["artifacts"][0]["parts"][0]["text"]["raw"]
                    analysis_data = json.loads(result_text)
                    
                    # Transform technical analysis into human advisor response
                    human_response = self._create_human_advisor_response(analysis_data, product_name)
                    
                    return {
                        'success': True,
                        'analysis': analysis_data,  # Keep raw data for metadata
                        'human_response': human_response,
                        'product_name': product_name,
                        'type': 'product_analysis'
                    }
                else:
                    error_msg = result.get('error', {}).get('message', 'Unknown error')
                    return {
                        'success': False,
                        'error': f"Analysis failed: {error_msg}",
                        'type': 'error'
                    }
            else:
                return {
                    'success': False,
                    'error': f"Coordinator request failed: {response.status_code}",
                    'type': 'error'
                }
                
        except Exception as e:
            logger.error(f"Product analysis failed: {e}")
            return {
                'success': False,
                'error': f"Failed to analyze product: {str(e)}",
                'type': 'error'
            }
    
    def _create_human_advisor_response(self, analysis_data: dict, product_name: str) -> str:
        """Transform technical analysis into human-like advisor response"""
        try:
            response_parts = []
            
            # Friendly opening
            response_parts.append(f"I've analyzed customer feedback for the **{product_name}** and here's what I found:")
            response_parts.append("")
            
            # Enhanced review collection summary with specific details
            workflow_metadata = analysis_data.get('workflow_metadata', {})
            scraping_metadata = workflow_metadata.get('scraping_metadata', {})
            
            # Check if we have detailed scraping information
            if scraping_metadata:
                sources_used = scraping_metadata.get('sources_scraped', [])
                total_reviews = scraping_metadata.get('total_reviews_collected', 0)
                review_breakdown = scraping_metadata.get('reviews_by_source', {})
                
                if sources_used and total_reviews > 0:
                    response_parts.append(f"📊 **Review Collection Summary:**")
                    response_parts.append(f"I collected **{total_reviews} customer reviews** for analysis:")
                    
                    for source in sources_used:
                        source_count = review_breakdown.get(source, 0)
                        source_name = "YouTube" if source.lower() == "youtube" else "Tiki" if source.lower() == "tiki" else source.title()
                        response_parts.append(f"  • **{source_name}**: {source_count} reviews")
                    
                    response_parts.append("")
                    response_parts.append("📝 **Sample of what customers are saying:**")
                    
                    # Add sample reviews if available
                    sample_reviews = scraping_metadata.get('sample_reviews', [])
                    if sample_reviews:
                        for i, review in enumerate(sample_reviews[:3], 1):  # Show max 3 samples
                            source = review.get('source', 'unknown').title()
                            text = review.get('text', '')[:120] + "..." if len(review.get('text', '')) > 120 else review.get('text', '')
                            response_parts.append(f"  **{i}. [{source} Review]**: \"{text}\"")
                    response_parts.append("")
                else:
                    response_parts.append(f"📊 **What I Found**: I analyzed available customer reviews to understand the real customer experience with this product.")
                    response_parts.append("")
            else:
                # Fallback: Try to extract source info from department analyses
                dept_analyses = analysis_data.get('department_analyses', [])
                if dept_analyses:
                    review_sources = set()
                    for dept in dept_analyses:
                        reasoning = dept.get('reasoning', '').lower()
                        if 'youtube' in reasoning:
                            review_sources.add('YouTube')
                        if 'tiki' in reasoning:
                            review_sources.add('Tiki')
                    
                    if review_sources:
                        source_text = " and ".join(review_sources)
                        response_parts.append(f"📊 **What I Found**: I collected and analyzed customer reviews from {source_text} to understand how people really feel about this product.")
                    else:
                        response_parts.append(f"📊 **What I Found**: I analyzed customer reviews to understand the real customer experience with this product.")
                    response_parts.append("")
            
            # Overall sentiment in human terms
            master_analysis = analysis_data.get('master_analysis', {})
            if master_analysis:
                sentiment = master_analysis.get('sentiment', 'mixed').lower()
                confidence = master_analysis.get('confidence', 0.0)
                reasoning = master_analysis.get('reasoning', '')
                
                # Convert sentiment to human language
                if sentiment == 'positive':
                    sentiment_desc = "customers generally love this product"
                elif sentiment == 'negative':
                    sentiment_desc = "customers have significant concerns"
                else:
                    sentiment_desc = "customers have mixed feelings"
                
                response_parts.append(f"🎯 **Overall Customer Sentiment**: Good news - {sentiment_desc}! Based on my analysis, I'm {confidence:.0%} confident in this assessment.")
                
                if reasoning:
                    response_parts.append(f"Here's why: {reasoning}")
                response_parts.append("")
            
            # Key insights from departments in human language
            if dept_analyses:
                response_parts.append("🔍 **Key Insights from Different Perspectives**:")
                
                for dept in dept_analyses:
                    agent_type = dept.get('agent_type', '').replace('_', ' ')
                    dept_sentiment = dept.get('sentiment', 'neutral')
                    dept_reasoning = dept.get('reasoning', '')
                    
                    # Humanize department names
                    dept_human_names = {
                        'quality': 'Product Quality',
                        'experience': 'User Experience', 
                        'user experience': 'Customer Experience',
                        'business': 'Business Impact',
                        'technical': 'Technical Performance'
                    }
                    
                    dept_name = dept_human_names.get(agent_type.lower(), agent_type.title())
                    
                    if dept_sentiment == 'positive':
                        emoji = "✅"
                    elif dept_sentiment == 'negative':
                        emoji = "⚠️"
                    else:
                        emoji = "🔄"
                    
                    response_parts.append(f"{emoji} **{dept_name}**: {dept_reasoning[:150]}{'...' if len(dept_reasoning) > 150 else ''}")
                
                response_parts.append("")
            
            # Business recommendations as actionable advice
            business_rec = analysis_data.get('business_recommendations', {})
            if business_rec:
                response_parts.append("💡 **My Recommendations for Your Business**:")
                response_parts.append("")
                
                business_impact = business_rec.get('business_impact', '')
                if business_impact:
                    # Make it more conversational
                    response_parts.append("Based on what customers are saying, here's what you should focus on:")
                    response_parts.append("")
                    response_parts.append(business_impact)
                    response_parts.append("")
                
                reasoning = business_rec.get('reasoning', '')
                if reasoning:
                    response_parts.append("**Why this matters for your business:**")
                    response_parts.append(reasoning)
                    response_parts.append("")
                
                # Add emotional and topic insights
                emotions = business_rec.get('emotions', [])
                topics = business_rec.get('topics', [])
                
                if emotions:
                    response_parts.append(f"🎭 **Customer Emotions**: Your customers are feeling: {', '.join(emotions[:5])}")
                
                if topics:
                    response_parts.append(f"🎯 **Priority Areas**: Focus on: {', '.join(topics[:5])}")
                
                response_parts.append("")
            
            # Friendly closing with next steps
            response_parts.append("🚀 **Next Steps**: I recommend prioritizing the issues that impact customer satisfaction most. Would you like me to dive deeper into any specific area or analyze a different product?")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Failed to create human advisor response: {e}")
            return f"I completed the analysis for {product_name}, but let me give you a simpler summary: Based on customer feedback, there are clear opportunities to improve this product. The main areas to focus on are customer experience and addressing the specific concerns mentioned in reviews. Would you like me to get more specific recommendations?"
    
    def handle_clarification_needed(self, original_message: str) -> Dict[str, Any]:
        """Handle case where user wants product analysis but no specific product mentioned"""
        return {
            'response': "I'd be happy to help you improve a product! Could you please specify which product you're asking about? For example, you could ask 'What should I improve for iPhone 14?' or 'How can I make my Samsung Galaxy better?'",
            'type': 'clarification_request',
            'suggestions': [
                "What should I improve for [product name]?",
                "How can I make my [product] better?",
                "Give me recommendations for [product name]"
            ]
        }
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Main method to process user message and return appropriate response
        
        Args:
            message: User's chat message
            
        Returns:
            dict: Formatted response for chat interface
        """
        try:
            # Analyze the message
            analysis = self.analyze_message(message)
            
            logger.info(f"Message analysis: {analysis}")
            
            if analysis['intent'] == 'general_chat':
                return self.handle_general_chat(message)
            
            elif analysis['intent'] == 'product_analysis':
                return self.handle_product_analysis(analysis['product_name'], message)
            
            elif analysis['intent'] == 'clarification_needed':
                return self.handle_clarification_needed(message)
            
            else:
                return {
                    'response': "I'm here to help! You can ask me general questions or request product improvement analysis.",
                    'type': 'fallback_response'
                }
                
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            return {
                'response': "I apologize, but I encountered an error processing your message. Please try again.",
                'type': 'error_response'
            } 