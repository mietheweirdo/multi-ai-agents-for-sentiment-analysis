import requests
import json

# URL of the running FastAPI server
url = "http://127.0.0.1:8000/tasks/send"

# Example: more complicated review comments for richer analysis
test_reviews = [
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

for idx, review in enumerate(test_reviews):
    payload = {
        "id": f"test-task-{idx+1}",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {"type": "text", "text": review}
                ]
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"\nReview {idx+1}: {review}")
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Error parsing response:", e)
