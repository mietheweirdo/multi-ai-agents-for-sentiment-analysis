import random

class AnalyzerAgent:
    def __init__(self, name="AnalyzerAgent", config=None):
        self.name = name
        self.config = config or {}
        # Example: self.api_key = self.config.get("api_key")
        # Example: self.model_name = self.config.get("model_name")

    def analyze(self, review):
        """
        Perform sentiment analysis on a review.
        Stub: randomly assigns sentiment and intensity, extracts key phrases.
        """
        text = review.get("review_text") or review.get("comment") or ""
        # Stub: Replace with GPT-4 or other LLM call
        sentiment = random.choice(["positive", "negative", "neutral"])
        intensity = random.choice(["strong", "moderate", "weak"])
        key_phrases = self.extract_key_phrases(text)
        return {
            "agent": self.name,
            "sentiment": sentiment,
            "intensity": intensity,
            "key_phrases": key_phrases,
            "text": text
        }

    def extract_key_phrases(self, text):
        # Very basic: split into words, pick a few as "key phrases"
        words = [w for w in text.split() if len(w) > 4]
        return words[:3]

    def debate(self, other_agent, review):
        """
        Debate protocol: both agents analyze and compare results.
        Returns a dict with both opinions and a simple resolution.
        """
        my_opinion = self.analyze(review)
        other_opinion = other_agent.analyze(review)
        # Simple debate: if sentiments differ, mark as "disagreement"
        if my_opinion["sentiment"] != other_opinion["sentiment"]:
            resolution = "disagreement"
        else:
            resolution = "agreement"
        return {
            "agent_1": my_opinion,
            "agent_2": other_opinion,
            "resolution": resolution
        }
