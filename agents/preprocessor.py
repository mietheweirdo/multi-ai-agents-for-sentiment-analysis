# agents/preprocessor.py
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class PreprocessorAgent:
    """Text normalization agent using LangChain and LLM (optional)."""
    def __init__(self, use_llm=False, config=None):
        self.use_llm = use_llm
        config = config or {}
        if use_llm:
            self.model_name = config.get("model_name")
            self.api_key = config.get("api_key")
            self.llm = ChatOpenAI(model=self.model_name, api_key=self.api_key)
            self.prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """
You are a Text Data Specialist at a leading e-commerce analytics company. Your job is to clean and normalize customer review text for downstream sentiment and trend analysis.

For each review, do the following:

1. Remove irrelevant symbols, emojis, and excessive whitespace.
2. Correct obvious typos and normalize spelling.
3. Ensure the text is clear, concise, and ready for automated analysis.

Return only the cleaned review text.
"""
                ),
                ("human", "Review: {review}")
            ])

    def clean(self, reviews):
        cleaned = []
        for r in reviews:
            text = r["text"].lower()
            text = re.sub(r"[^a-z0-9\s]", "", text)
            if self.use_llm:
                prompt = self.prompt.format(review=text)
                result = self.llm.invoke(prompt)
                text = result.content.strip()
            cleaned.append({**r, "cleaned_text": text})
        return cleaned
