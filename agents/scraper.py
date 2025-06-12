# agents/scraper.py
class ScraperAgent:
    """Data Acquisition Specialist: Responsible for collecting customer reviews from e-commerce sources with care for data quality and rate limits."""
    def __init__(self, persona=None):
        self.persona = persona or "You are a Data Acquisition Specialist. Your job is to gather customer reviews from online sources, ensuring data completeness and respecting API rate limits."
        # Product-specific shoe reviews for demo/testing
        self._reviews = [
            {"review_id": 1, "text": "These running shoes are incredibly comfortable and lightweight. My feet don't hurt even after hours of jogging. Love the breathable material!"},
            {"review_id": 2, "text": "The shoes look stylish but the sole started coming off after just two weeks. Disappointed with the quality."},
            {"review_id": 3, "text": "Great value for the price. The grip is excellent and they fit perfectly. Will buy again for my family."},
            {"review_id": 4, "text": "I ordered a size 9 but received a size 8. Customer service was quick to resolve the issue, but the process was a hassle."},
            {"review_id": 5, "text": "The color is vibrant and matches the pictures. However, the laces are too short and keep coming undone."},
            {"review_id": 6, "text": "After a month of use, the shoes still look brand new. Very satisfied with the durability."},
            {"review_id": 7, "text": "The arch support is lacking, which caused discomfort during long walks. Would not recommend for people with flat feet."},
            {"review_id": 8, "text": "Delivery was delayed by a week, but the seller kept me updated. Packaging was secure."},
            {"review_id": 9, "text": "My son loves these shoes for his basketball games. He says they help him jump higher and run faster!"},
            {"review_id": 10, "text": "The shoes have a strong chemical smell out of the box. It faded after a few days, but it was unpleasant at first."}
        ]

    def set_reviews(self, reviews):
        print("[ScraperAgent] Setting reviews (count:", len(reviews), ")")
        # Accepts a list of dicts or strings (if strings, wrap as dicts)
        if reviews and isinstance(reviews[0], str):
            self._reviews = [{"review_id": i+1, "text": r} for i, r in enumerate(reviews)]
        else:
            self._reviews = reviews
        print("[ScraperAgent] Reviews set (count:", len(self._reviews), ")")

    def get_reviews(self, product_id=None):
        print("[ScraperAgent] Getting reviews (count:", len(self._reviews), ")")
        return self._reviews
