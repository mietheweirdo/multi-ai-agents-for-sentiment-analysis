# agents/analyzer.py
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class AnalyzerAgent:
    """LLM-based sentiment analyzer using OpenAI GPT-4 via LangChain. Supports persona/focus for diverse perspectives."""
    def __init__(self, config=None, persona=None):
        self.config = config or {}
        self.persona = persona or "You are a Customer Insights Analyst. Analyze product reviews for sentiment, emotions, and topics."
        self.model_name = self.config.get("model_name")
        self.api_key = self.config.get("api_key")
        self.llm = ChatOpenAI(model=self.model_name, api_key=self.api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.persona + "\nAnalyze the following review. Identify: 1) sentiment (positive/neutral/negative), 2) emotions, 3) facets/topics, 4) facet→emotions mapping, and 5) a short explanation. Return as JSON: {sentiment, emotions, facets, facet_emotions, explanation}"),
            ("human", "Review: {review}")
        ])

    def analyze(self, reviews):
        results = []
        for review in reviews:
            print(f"[AnalyzerAgent:{self.persona.split('.')[0]}] Analyzing review: {review.get('text', review)}")
            result = self._analyze_single(review)
            print(f"[AnalyzerAgent:{self.persona.split('.')[0]}] Result: {result}")
            results.append(result)
        return results

    def _analyze_single(self, review):
        text = review["text"] if isinstance(review, dict) else review
        try:
            prompt = self.prompt.format(review=text)
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
        except Exception as e:
            result = {
                "sentiment": "Unknown",
                "emotions": [],
                "facets": [],
                "facet_emotions": {},
                "explanation": f"Error: {str(e)}"
            }
        return result
