# main.py
from agents.coordinator import CoordinatorAgent

def main():
    coordinator = CoordinatorAgent()
    report = coordinator.run_workflow(product_id="mock123")
    print("=== Sentiment Analysis Report ===")
    print(f"Total reviews: {report['total_reviews']}")
    print(f"Summary: {report['summary']}")
    print(f"Insight: {report['insight']}")

if __name__ == "__main__":
    main()
