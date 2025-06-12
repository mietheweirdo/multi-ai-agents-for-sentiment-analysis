# agents/analyzer.py
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class AnalyzerAgent:
    """LLM-based sentiment analyzer using OpenAI GPT-4 via LangChain. Supports persona/focus for diverse perspectives."""
    def __init__(self, config=None, persona=None):
        config = config or {}
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        self.persona = persona or (
            "You are a Senior Customer Insights Analyst at a leading e-commerce company. Your job is to deeply understand customer feedback and extract actionable business intelligence from product reviews."
        )
        self.llm = ChatOpenAI(model=self.model_name, api_key=self.api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                self.persona + "\n\nFor the following product review, extract:\n1. Overall sentiment (positive, neutral, negative)\n2. List of emotions expressed (e.g., happy, frustrated, excited, disappointed, etc.)\n3. List of product facets/topics mentioned (e.g., quality, delivery, style, comfort, price, customer service, etc.)\n4. For each facet/topic, map the emotions expressed about it (facet→emotions mapping).\n\nReturn a JSON object with keys: sentiment, emotions, facets, facet_emotions (dict), and a short explanation."
            ),
            ("human", "Review: {review}")
        ])

    def analyze(self, reviews):
        print(f"[AnalyzerAgent] ({self.persona.split('.')[0]}) Analyzing {len(reviews)} review(s)...")
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
        print(f"[AnalyzerAgent] ({self.persona.split('.')[0]}) Result: {result}")
        print(f"[AnalyzerAgent] Analysis complete.")
        return results