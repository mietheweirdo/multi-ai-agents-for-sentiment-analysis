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
        for idx, r in enumerate(reviews):
            text = r["cleaned_text"] if "cleaned_text" in r else r["text"]
            print(f"[AnalyzerAgent] Review {idx+1}: {text[:60]}...")
            prompt = self.prompt.format(review=text)
            try:
                print(f"[AnalyzerAgent] Invoking LLM for review {idx+1}...")
                result = self.llm.invoke(prompt)
                content = result.content.strip()
                # Try to extract JSON from the response
                json_start = content.find('{')
                json_end = content.rfind('}')
                if json_start != -1 and json_end != -1:
                    content_json = content[json_start:json_end+1]
                    parsed = json.loads(content_json)
                else:
                    # Fallback: try to parse as is
                    parsed = json.loads(content)
                # Ensure required keys
                sentiment = parsed.get("sentiment", "neutral")
                emotions = parsed.get("emotions", [])
                facets = parsed.get("facets", [])
                facet_emotions = parsed.get("facet_emotions", {})
                explanation = parsed.get("explanation", "")
                # Defensive: ensure types
                if not isinstance(emotions, list):
                    emotions = [emotions] if emotions else []
                if not isinstance(facets, list):
                    facets = [facets] if facets else []
                if not isinstance(facet_emotions, dict):
                    facet_emotions = {}
                result = {
                    **r,
                    "sentiment": sentiment,
                    "emotions": emotions,
                    "facets": facets,
                    "facet_emotions": facet_emotions,
                    "explanation": explanation,
                }
                print(f"[AnalyzerAgent:{self.persona.split('.')[0]}] Result: {result}")
                results.append(result)
            except Exception as e:
                print(f"[AnalyzerAgent] Error analyzing review {idx+1}: {e}")
                # Fallback: return neutral with error info
                results.append({
                    **r,
                    "sentiment": "neutral",
                    "emotions": [],
                    "facets": [],
                    "facet_emotions": {},
                    "explanation": f"AnalyzerAgent error: {str(e)}"
                })
        print(f"[AnalyzerAgent] Analysis complete.")
        return results
