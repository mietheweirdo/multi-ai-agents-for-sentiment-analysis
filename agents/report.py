class ReportAgent:
    def __init__(self, config=None):
        # Store config for future use if needed
        self.config = config or {}

    def compile(self, product_analysis):
        """
        Compile the product analysis results into a structured report.
        Accepts either a dict of product analyses or a single product analysis.
        """
        if not product_analysis:
            return {"error": "No analysis data provided."}

        # If input is a dict of products, summarize each
        if isinstance(product_analysis, dict):
            report = {
                "products": []
            }
            for product_id, analysis in product_analysis.items():
                report["products"].append(self._summarize_product(product_id, analysis))
            return report

        # If input is a single product analysis
        return self._summarize_product(product_analysis.get("product_id", "unknown"), product_analysis)

    def _summarize_product(self, product_id, analysis):
        """
        Summarize a single product's analysis.
        """
        return {
            "product_id": analysis.get("product_id", product_id),
            "product_name": analysis.get("product_name", ""),
            "overall_sentiment": analysis.get("overall_sentiment", ""),
            "sentiment_distribution": analysis.get("sentiment_distribution", {}),
            "key_strengths": analysis.get("key_strengths", []),
            "key_weaknesses": analysis.get("key_weaknesses", []),
            "recurring_themes": analysis.get("recurring_themes", []),
            "business_recommendations": analysis.get("business_recommendations", []),
            "confidence": analysis.get("confidence", 0)
        }
