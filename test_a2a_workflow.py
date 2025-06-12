import requests
import json

# URL of the running FastAPI server
url = "http://127.0.0.1:8000/tasks/send"

# Product-specific shoe reviews
reviews = [
    "These running shoes are incredibly comfortable and lightweight. My feet don't hurt even after hours of jogging. Love the breathable material!",
    "The shoes look stylish but the sole started coming off after just two weeks. Disappointed with the quality.",
    "Great value for the price. The grip is excellent and they fit perfectly. Will buy again for my family.",
    "I ordered a size 9 but received a size 8. Customer service was quick to resolve the issue, but the process was a hassle.",
    "The color is vibrant and matches the pictures. However, the laces are too short and keep coming undone.",
    "After a month of use, the shoes still look brand new. Very satisfied with the durability.",
    "The arch support is lacking, which caused discomfort during long walks. Would not recommend for people with flat feet.",
    "Delivery was delayed by a week, but the seller kept me updated. Packaging was secure.",
    "My son loves these shoes for his basketball games. He says they help him jump higher and run faster!",
    "The shoes have a strong chemical smell out of the box. It faded after a few days, but it was unpleasant at first."
]

payload = {
    "id": "test-batch-shoes",
    "params": {
        "message": {
            "role": "user",
            "parts": [
                {"type": "text", "text": r} for r in reviews
            ]
        }
    }
}
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(payload), headers=headers)

print("\n=== DEBUG: Payload Sent ===")
print(json.dumps(payload, indent=2))
print("\nBatch Review Analysis for Shoes Product")
print("Status Code:", response.status_code)
print("\n=== DEBUG: Raw Response Text ===")
print(response.text)
try:
    data = response.json()
    print("\n=== DEBUG: Parsed JSON Response ===")
    print(json.dumps(data, indent=2))
    # Print key fields for quick inspection
    if 'per_review' in data:
        print("\n=== Per-Review Analysis (truncated) ===")
        for i, review in enumerate(data['per_review'][:3]):
            print(f"Review {i+1}: {json.dumps(review, indent=2)}")
    if 'discussion_history' in data:
        print("\n=== Discussion History (truncated) ===")
        print(json.dumps(data['discussion_history'][:3], indent=2))
    if 'summary' in data:
        print("\n=== Summary ===\n", data['summary'])
    if 'recommendations' in data:
        print("\n=== Recommendations ===\n", data['recommendations'])
except Exception as e:
    print("\n[DEBUG] Could not parse JSON response:", e)
