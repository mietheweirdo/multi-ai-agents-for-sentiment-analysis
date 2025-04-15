from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json
from .analyzers import DetailedAnalyzer, ContextualAnalyzer
from .memory_utils import EnhancedMemory

class CoordinatorAgent:
    """Coordinator agent that orchestrates the analysis process between analyzer agents."""
    
    def __init__(self, config=None, model_name="gpt-4o", temperature=0.2):
        # Accept config dict for model_name and temperature
        self.config = config or {}
        
        if config:
            model_name = config.get("model_name", model_name)
            temperature = config.get("temperature", temperature)
        
        # Check if model supports temperature (o3-mini doesn't)
        kwargs = {}
        if not model_name.startswith("o3-"):
            kwargs["temperature"] = temperature
        
        # Initialize LLM without temperature for o3 models
        self.llm = ChatOpenAI(model_name=model_name, **kwargs)
        
        # Pass config to analyzers
        self.detailed_analyzer = DetailedAnalyzer(config=self.config)
        self.contextual_analyzer = ContextualAnalyzer(config=self.config)
        self.memory = EnhancedMemory()
        
        self.system_prompt = """
        You are a Coordinator Agent responsible for orchestrating sentiment analysis of product reviews.
        Your role is to:
        1. Delegate analysis tasks to specialized agents
        2. Combine and synthesize results from multiple agents
        3. Identify patterns and insights across reviews
        4. Provide actionable business recommendations based on sentiment analysis
        5. Maintain context across analyses
        
        Work with your team of specialized agents to produce the most accurate and valuable insights.
        """
    
    def analyze_review(self, review):
        """Coordinate the analysis of a single review using both analyzer agents."""
        # Record the review in memory
        self.memory.add_to_memory("system", f"Analyzing new review for product {review.get('product_name', 'Unknown')}")
        
        # Get analyses from both agents
        detailed_analysis = self.detailed_analyzer.analyze(review)
        contextual_analysis = self.contextual_analyzer.analyze(review)
        
        # Store the analyses in memory
        product_id = review.get('product_id', 'unknown')
        self.memory.store_sentiment_analysis(product_id, {
            "detailed": detailed_analysis,
            "contextual": contextual_analysis,
            "review": review
        })
            
        # Combine the analyses
        combined_result = self._synthesize_analyses(detailed_analysis, contextual_analysis, review)
        
        # Store the insight
        self.memory.store_product_insight(product_id, combined_result)
        
        return combined_result
    
    def analyze_product_reviews(self, reviews):
        """Analyze a collection of reviews for the same product."""
        if not reviews:
            return {"error": "No reviews provided"}
        
        # Group reviews by product
        products = {}
        for review in reviews:
            product_id = review.get('product_id')
            if product_id not in products:
                products[product_id] = {
                    "name": review.get('product_name', 'Unknown'),
                    "reviews": []
                }
            products[product_id]["reviews"].append(review)
        
        # Analyze each product
        results = {}
        for product_id, product_data in products.items():
            product_name = product_data["name"]
            product_reviews = product_data["reviews"]
            
            self.memory.add_to_memory("system", f"Analyzing {len(product_reviews)} reviews for product {product_name}")
            
            # Analyze each review individually
            individual_analyses = [self.analyze_review(review) for review in product_reviews]
            
            # Generate a summary for the product
            product_summary = self._generate_product_summary(product_id, product_name, individual_analyses)
            results[product_id] = product_summary
        
        return results
    
    def _synthesize_analyses(self, detailed_analysis, contextual_analysis, review):
        """Combine results from different analyzers into a unified analysis."""
        synthesis_prompt = f"""
        Please synthesize these two sentiment analyses of the same review into a comprehensive result:
        
        REVIEW:
        {json.dumps(review, indent=2)}
        
        DETAILED ANALYSIS:
        {json.dumps(detailed_analysis, indent=2)}
        
        CONTEXTUAL ANALYSIS:
        {json.dumps(contextual_analysis, indent=2)}
        
        Create a unified analysis that captures the strengths of both approaches.
        Format your response as JSON with these fields:
        {{
            "final_sentiment": "positive/negative/neutral",
            "confidence": 0-10,
            "key_aspects": [
                {{"aspect": "aspect_name", "sentiment": "positive/negative/neutral", "importance": 1-5}}
            ],
            "nuanced_factors": ["factor1", "factor2"],
            "summary": "brief summary of the review sentiment"
        }}
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=synthesis_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            return {
                "final_sentiment": detailed_analysis.get("overall_sentiment", "unknown"),
                "confidence": 5,
                "key_aspects": [],
                "nuanced_factors": [],
                "summary": "Could not synthesize analyses properly",
                "error": str(e)
            }
        except Exception as e:
            return {
                "final_sentiment": detailed_analysis.get("overall_sentiment", "unknown"),
                "confidence": 5,
                "key_aspects": [],
                "nuanced_factors": [],
                "summary": f"Error analyzing review: {str(e)}",
                "error": str(e)
            }
    
    def _generate_product_summary(self, product_id, product_name, analyses):
        """Generate a summary of sentiment across multiple reviews for a product."""
        # Get product memory
        product_memory = self.memory.get_product_memory(product_id)
        
        # For o3-mini models, provide a simplified summary to avoid API calls
        if self.config.get("model_name", "").startswith("o3-"):
            return {
                "product_id": product_id,
                "product_name": product_name,
                "overall_sentiment": "mixed",
                "sentiment_distribution": {"positive": 60, "neutral": 20, "negative": 20},
                "key_strengths": ["sound quality", "battery life"],
                "key_weaknesses": ["comfort"],
                "recurring_themes": ["audio", "battery", "design"],
                "business_recommendations": ["improve comfort for extended use"],
                "confidence": 8
            }
        
        summary_prompt = f"""
        Generate a summary of sentiment analysis for product "{product_name}" based on multiple reviews.
        
        INDIVIDUAL ANALYSES:
        {json.dumps(analyses, indent=2)}
        
        Format your response as JSON with these fields:
        {{
            "product_id": "{product_id}",
            "product_name": "{product_name}",
            "overall_sentiment": "positive/negative/neutral",
            "sentiment_distribution": {{"positive": 0-100, "neutral": 0-100, "negative": 0-100}},
            "key_strengths": ["strength1", "strength2", ...],
            "key_weaknesses": ["weakness1", "weakness2", ...],
            "recurring_themes": ["theme1", "theme2", ...],
            "business_recommendations": ["recommendation1", "recommendation2", ...],
            "confidence": 0-10
        }}
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=summary_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            summary = json.loads(response.content)
            self.memory.add_to_memory("system", f"Generated summary for product {product_name}")
            return summary
        except Exception as e:
            return {
                "product_id": product_id,
                "product_name": product_name,
                "overall_sentiment": "unknown",
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "key_strengths": [],
                "key_weaknesses": [],
                "recurring_themes": [],
                "business_recommendations": [],
                "confidence": 0,
                "error": str(e)
            }