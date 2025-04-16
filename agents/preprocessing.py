import copy

class PreprocessingAgent:
    def __init__(self, config=None):
        # Store config for future use if needed
        self.config = config or {}
    
    def preprocess(self, reviews):
        """
        Cleans and normalizes a list of review dicts.
        For demonstration: lowercases and strips text fields.
        """
        cleaned_reviews = []
        for review in reviews:
            cleaned = copy.deepcopy(review)
            # Normalize possible text fields
            if "review_text" in cleaned and isinstance(cleaned["review_text"], str):
                cleaned["review_text"] = cleaned["review_text"].strip().lower()
            if "comment" in cleaned and isinstance(cleaned["comment"], str):
                cleaned["comment"] = cleaned["comment"].strip().lower()
            cleaned_reviews.append(cleaned)
        return cleaned_reviews
