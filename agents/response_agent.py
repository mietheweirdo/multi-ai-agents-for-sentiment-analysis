# agents/response_agent.py
"""
Response Agent for generating user-friendly chatbot responses
Synthesizes LangGraph analysis results into natural conversational responses
"""

import json
import re
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
        
        # Response generation prompt with language awareness
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a smart product assistant that provides helpful, natural responses about products.

Your task is to synthesize multi-agent analysis results into a single, readable answer for users.

IMPORTANT: You must respond in the SAME LANGUAGE as the user's input question.
- If the user writes in Vietnamese, respond entirely in Vietnamese
- If the user writes in English, respond entirely in English  
- If the input is mixed language, respond in the dominant language detected

Guidelines:
- Give direct, helpful answers to user questions
- Use information from the analysis to support your response
- Keep responses conversational and easy to understand
- If it's purchase advice, be balanced and mention key considerations
- If it's about improvements, provide practical suggestions based on user feedback
- Always sound confident but not overly promotional
- Don't mention "agents" or "analysis" - just give natural advice
- Match the user's language and cultural context

Response should be 2-4 sentences, clear and actionable."""),
            ("human", """{context}

USER QUESTION LANGUAGE: {detected_language}

Based on this analysis, provide a natural, helpful response to the user's question: "{user_question}"

Remember: Respond in {language_instruction} to match the user's input language. Make it sound like you're a knowledgeable friend giving advice, not a technical report.""")
        ])
        
        self.chain = self.prompt | self.llm
    
    def _detect_language(self, text: str) -> tuple[str, str]:
        """
        Detect the language of the input text and return language code and instruction.
        Returns (language_code, language_instruction)
        """
        if not text:
            return 'en', 'English'
        
        # Vietnamese character patterns
        vietnamese_chars = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]'
        vietnamese_count = len(re.findall(vietnamese_chars, text, re.IGNORECASE))
        vietnamese_ratio = vietnamese_count / len(text) if text else 0
        
        # Check for Vietnamese words and phrases
        vietnamese_words = [
            'là', 'của', 'có', 'được', 'này', 'một', 'cho', 'với', 'tôi', 'sản phẩm', 
            'chất lượng', 'giá', 'mua', 'bán', 'đánh giá', 'review', 'tốt', 'xấu', 
            'nên', 'không', 'rất', 'quá', 'khá', 'hơi', 'cực', 'siêu', 'điện thoại',
            'laptop', 'máy tính', 'thích', 'ghét', 'yêu', 'ưng', 'ổn', 'tệ'
        ]
        
        vietnamese_word_count = 0
        for word in vietnamese_words:
            if word in text.lower():
                vietnamese_word_count += text.lower().count(word)
        
        # English word detection
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)
        english_ratio = len(english_words) / len(text.split()) if text.split() else 0
        
        # Decision logic
        if vietnamese_ratio >= 0.1 or vietnamese_word_count >= 2:
            return 'vi', 'Vietnamese (tiếng Việt)'
        elif english_ratio >= 0.6:
            return 'en', 'English'
        else:
            # If mixed or unclear, default to the language with more indicators
            if vietnamese_word_count > 0:
                return 'vi', 'Vietnamese (tiếng Việt)'
            else:
                return 'en', 'English'
    
    def generate_response(self, 
                         analysis_result: Dict[str, Any], 
                         user_input: str, 
                         product_name: str, 
                         question_type: str, 
                         scraped_data: List[Dict]) -> str:
        """Generate final user response from analysis results"""
        
        try:
            # Detect the language of user input
            detected_lang, language_instruction = self._detect_language(user_input)
            
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
                    review_text = review.get('content', review.get('review_text', ''))[:150]
                    if review_text:
                        context += f"- Review {i+1}: {review_text}...\n"
            
            # Generate the response with language awareness
            response = self.chain.invoke({
                "context": context,
                "user_question": user_input,
                "detected_language": detected_lang,
                "language_instruction": language_instruction
            })
            
            return response.content.strip()
            
        except Exception as e:
            print(f"⚠️ Response generation failed: {e}")
            
            # Language-aware intelligent fallback based on question type and product
            detected_lang, _ = self._detect_language(user_input)
            
            if detected_lang == 'vi':
                # Vietnamese fallbacks
                if question_type == "purchase_advice":
                    return f"Dựa trên phân tích thị trường hiện tại, {product_name} có cả điểm mạnh và những cân nhắc. Tôi khuyên bạn nên đánh giá xem sản phẩm có phù hợp với nhu cầu và ngân sách cụ thể của mình không trước khi quyết định mua."
                
                elif question_type == "improvement_suggestions":
                    return f"{product_name} có thể được cải thiện về trải nghiệm người dùng, tối ưu hóa hiệu suất và giải quyết các phản hồi thường gặp từ khách hàng. Các lĩnh vực chính cần cải thiện có vẻ tập trung vào khả năng sử dụng và tinh chỉnh tính năng."
                
                elif question_type == "comparison":
                    return f"Khi so sánh {product_name} với các lựa chọn khác, hãy xem xét các yếu tố như trường hợp sử dụng, ngân sách và nhu cầu dài hạn của bạn. Mỗi lựa chọn đều có điểm mạnh riêng trong các lĩnh vực khác nhau."
                
                else:
                    return f"Cảm ơn bạn đã hỏi về {product_name}! Mặc dù tôi rất muốn đưa ra câu trả lời chi tiết, tôi khuyên bạn nên kiểm tra các đánh giá gần đây và ý kiến chuyên gia để có cái nhìn cập nhất về sản phẩm này."
            
            else:
                # English fallbacks (original)
                if question_type == "purchase_advice":
                    return f"Based on current market analysis, {product_name} has both strengths and considerations. I'd recommend evaluating how it fits your specific needs and budget before making a decision."
                
                elif question_type == "improvement_suggestions":
                    return f"{product_name} could benefit from enhancements in user experience, performance optimization, and addressing common user feedback. The key areas for improvement seem to be around usability and feature refinement."
                
                elif question_type == "comparison":
                    return f"When comparing {product_name} with alternatives, consider factors like your use case, budget, and long-term needs. Each option has its own strengths in different areas."
                
                else:
                    return f"Thanks for asking about {product_name}! While I'd love to give you a detailed answer, I recommend checking recent reviews and expert opinions for the most current insights on this product."
