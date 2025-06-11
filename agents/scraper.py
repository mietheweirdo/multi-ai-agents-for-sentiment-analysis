# agents/scraper.py
class ScraperAgent:
    """Data Acquisition Specialist: Responsible for collecting customer reviews from e-commerce sources with care for data quality and rate limits."""
    def get_reviews(self, product_id=None):
        # System prompt (for future LLM-based scraping):
        # """
        # You are a Data Acquisition Specialist. Your job is to gather customer reviews from online sources, ensuring data completeness and respecting API rate limits.
        # """
        # Return mock reviews
        return [
            {"review_id": 1, "text": "Great product, fast shipping!", "rating": 5},
            {"review_id": 2, "text": "Not as described, disappointed.", "rating": 2},
            {"review_id": 3, "text": "Average quality, okay for the price.", "rating": 3},
        ]
