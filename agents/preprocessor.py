# agents/preprocessor.py
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class PreprocessorAgent:
    """Text normalization agent using LangChain and LLM (optional)."""
    def __init__(self, use_llm=False, config=None, persona=None):
        self.use_llm = use_llm
        self.persona = persona or "You are a Text Data Specialist at a leading e-commerce analytics company. Your job is to clean and normalize customer review text for downstream sentiment and trend analysis."
        config = config or {}
        if use_llm:
            self.model_name = config.get("model_name")
            self.api_key = config.get("api_key")
            self.llm = ChatOpenAI(model=self.model_name, api_key=self.api_key)
            self.prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    self.persona + "\n\nFor each review, do the following:\n\n1. Remove irrelevant symbols, emojis, and excessive whitespace.\n2. Correct obvious typos and normalize spelling.\n3. Ensure the text is clear, concise, and ready for automated analysis.\n\nReturn only the cleaned review text."
                ),
                ("human", "Review: {review}")
            ])

    def clean(self, reviews):
        print(f"[PreprocessorAgent] Cleaning {len(reviews)} reviews...")
        cleaned = []
        for i, r in enumerate(reviews):
            text = r["text"].lower()
            text = re.sub(r"[^a-z0-9\s]", "", text)
            if self.use_llm:
                print(f"[PreprocessorAgent] Cleaning review {i+1} with LLM...")
                prompt = self.prompt.format(review=text)
                result = self.llm.invoke(prompt)
                text = result.content.strip()
            cleaned_review = {**r, "cleaned_text": text}
            cleaned.append(cleaned_review)
        print(f"[PreprocessorAgent] Cleaning complete.")
        return cleaned
