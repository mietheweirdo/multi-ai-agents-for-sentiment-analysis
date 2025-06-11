# agents/analyzer.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class AnalyzerAgent:
    """LLM-based sentiment analyzer using OpenAI GPT-4 via LangChain."""
    def __init__(self, config=None):
        config = config or {}
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        self.llm = ChatOpenAI(model=self.model_name, api_key=self.api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are a Senior Customer Insights Analyst at a leading e-commerce company. Your job is to deeply understand customer feedback and extract actionable business intelligence from product reviews.

For each review, do the following:

1. Classify the overall sentiment as Positive, Negative, or Neutral.

2. Identify and list any specific emotions expressed (e.g., joy, frustration, disappointment, excitement, gratitude, etc.).

3. Extract any notable topics or trends mentioned in the review (e.g., product quality, delivery, customer service, price, packaging, etc.).

4. For each topic, map the most relevant emotion(s) expressed about that topic (if any). Return as a dictionary: topic -> [emotions].

5. Provide a short explanation for your sentiment classification.

6. Go beyond star ratings: Look for subtle cues, recurring patterns, and emerging issues or opportunities in the feedback.

Return your answer in this JSON format:
{{
  "sentiment": ...,
  "emotions": [...],
  "topics": [...],
  "topic_emotions": {{topic1: [emotions], ...}},
  "explanation": ...
}}
"""
            ),
            ("human", "Review: {review}")
        ])

    def analyze(self, reviews):
        analyzed = []
        for r in reviews:
            text = r["cleaned_text"]
            prompt = self.prompt.format(review=text)
            result = self.llm.invoke(prompt)
            try:
                parsed = self._parse_json_response(result.content)
            except Exception:
                sentiment, explanation = self._parse_response(result.content)
                parsed = {"sentiment": sentiment, "emotions": [], "topics": [], "topic_emotions": {}, "explanation": explanation}
            analyzed.append({**r, **parsed})
        return analyzed

    def _parse_json_response(self, response):
        import json
        data = json.loads(response)
        sentiment = data.get("sentiment", "Unknown")
        emotions = data.get("emotions", [])
        topics = data.get("topics", [])
        topic_emotions = data.get("topic_emotions", {})
        explanation = data.get("explanation", response)
        return {"sentiment": sentiment, "emotions": emotions, "topics": topics, "topic_emotions": topic_emotions, "explanation": explanation}

    def _parse_response(self, response):
        # Simple parsing: expects 'Sentiment: ... Explanation: ...'
        sentiment = "Unknown"
        explanation = response
        if "Sentiment:" in response:
            parts = response.split("Sentiment:")[-1].split("Explanation:")
            sentiment = parts[0].strip()
            if len(parts) > 1:
                explanation = parts[1].strip()
        return sentiment, explanation
