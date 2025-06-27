"""
Base prompts and utilities for the multi-agent sentiment analysis system.
Contains common templates and helper functions used across all agents.
"""

from typing import Dict, List, Any

class BasePrompts:
    """Base prompt templates and utilities"""
    
    # Common system message template
    SYSTEM_TEMPLATE = """You are an AI assistant specialized in sentiment analysis.
Your task is to analyze product reviews and provide detailed sentiment insights.
Always respond in a structured, professional manner."""

    # Common human message template for sentiment analysis
    HUMAN_TEMPLATE = """Review: {review}

Analyze this review and respond with a JSON object containing:
- sentiment: positive/neutral/negative
- confidence: confidence score from 0.0 to 1.0
- emotions: list of emotions detected
- topics: key topics/facets mentioned
- reasoning: brief reasoning for sentiment (max 100 words)
- business_impact: business impact assessment (max 50 words)"""

    # Error handling template
    ERROR_TEMPLATE = """Analysis Error: {error_message}

Please provide a fallback analysis with:
- sentiment: neutral
- confidence: 0.5
- emotions: []
- topics: []
- reasoning: "Unable to analyze due to error"
- business_impact: "Unable to assess" """

    # Token limit warning
    TOKEN_LIMIT_WARNING = """IMPORTANT: You have a token limit of {max_tokens} tokens.
Keep your responses concise and focused on the most important aspects.
Prioritize accuracy over verbosity."""

    @staticmethod
    def format_confidence_score(score: float) -> str:
        """Format confidence score for display"""
        if score >= 0.8:
            return "Very High"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low"

    @staticmethod
    def validate_sentiment(sentiment: str) -> str:
        """Validate and normalize sentiment value"""
        valid_sentiments = ["positive", "neutral", "negative"]
        normalized = sentiment.lower().strip()
        return normalized if normalized in valid_sentiments else "neutral"

    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    @staticmethod
    def format_agent_output(output: Dict[str, Any]) -> Dict[str, Any]:
        """Format and validate agent output"""
        formatted = {
            "sentiment": BasePrompts.validate_sentiment(output.get("sentiment", "neutral")),
            "confidence": max(0.0, min(1.0, float(output.get("confidence", 0.5)))),
            "emotions": output.get("emotions", []),
            "topics": output.get("topics", []),
            "reasoning": BasePrompts.truncate_text(output.get("reasoning", ""), 500),
            "business_impact": BasePrompts.truncate_text(output.get("business_impact", ""), 500)
        }
        return formatted 