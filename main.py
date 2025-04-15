import os
import json
# Remove dotenv import
# from dotenv import load_dotenv
from agents.coordinator import CoordinatorAgent
from agents.scraper import ScraperAgent
from agents.preprocessing import PreprocessingAgent
from agents.report import ReportAgent
from agents.gpt_handler import GPTHandler
from data.sample_reviews import SHOPEE_REVIEWS, YOUTUBE_REVIEWS

# Load config from config.json
def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def main():
    """Main function to run the sentiment analysis system."""
    print("Starting Multi-Agent Sentiment Analysis System")
    print("=============================================")

    # Load configuration
    config = load_config()

    # Step 1: Scrape data from sources
    scraper = ScraperAgent()
    sources = [SHOPEE_REVIEWS, YOUTUBE_REVIEWS]
    scraped_reviews = []
    for source in sources:
        scraped_reviews.extend(scraper.scrape(source))

    # Step 2: Preprocess scraped data
    preprocessor = PreprocessingAgent()
    preprocessed_reviews = preprocessor.preprocess(scraped_reviews)

    # Step 3: Initialize the coordinator agent (pass config if needed)
    coordinator = CoordinatorAgent(config=config)

    # Step 4: Select a product for analysis
    product_id = "S001"  # Wireless Earbuds

    # Step 5: Filter reviews for the selected product
    product_reviews = [review for review in preprocessed_reviews if review["product_id"] == product_id]

    print(f"Analyzing {len(product_reviews)} reviews for product ID: {product_id}")

    # Step 6: Analyze individual review for detailed view
    sample_review = product_reviews[0]
    print("\nDetailed analysis of a single review:")
    print(f"Review: {sample_review.get('review_text', sample_review.get('comment', ''))}")

    single_analysis = coordinator.analyze_review(sample_review)
    print(json.dumps(single_analysis, indent=2))

    # Step 7: Analyze all reviews for the product
    print("\nAnalyzing all reviews for the product...")
    product_analysis = coordinator.analyze_product_reviews(product_reviews)

    # Step 8: Compile report using ReportAgent
    report_agent = ReportAgent()
    report = report_agent.compile(product_analysis)

    # Step 9: Generate human-readable summary using GPTHandler (pass config)
    gpt_handler = GPTHandler(config=config)
    summary = gpt_handler.generate_summary(report)

    # Display the results
    print("\nProduct Sentiment Analysis Summary:")
    print(json.dumps(report, indent=2))
    print("\nGPT-Generated Summary:")
    print(summary)

    # Show how the memory agent has stored information
    print("\nMemory Agent - Stored Insights:")
    product_memory = coordinator.memory.get_product_memory(product_id)
    print(f"Number of stored insights: {len(product_memory['insights'])}")
    print(f"Number of sentiment analyses: {len(product_memory['sentiment_history'])}")

    print("\nMulti-Agent Sentiment Analysis Complete")

if __name__ == "__main__":
    main()