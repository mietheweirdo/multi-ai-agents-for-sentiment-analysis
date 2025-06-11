import requests
import json

# URL of the running FastAPI server
url = "http://127.0.0.1:8000/tasks/send"

# Example: more complicated review comments for richer analysis
test_reviews = [
    "The product arrived on time but the packaging was damaged. The item itself works fine, but I expected better quality for the price.",
    "Absolutely love it! The color is vibrant and it fits perfectly. Will definitely buy again.",
    "Customer service was unhelpful when I reported a missing part. Not sure if I would recommend this to others.",
    "It's okay, not great. Some features are useful, but others are confusing and the manual is hard to follow.",
    "I bought this for my mom and she was thrilled! She said it made her day. Thank you!",
    "The product stopped working after a week. Very disappointed. I wish I could get a refund.",
    "Surprisingly good for the price. There are a few minor issues, but overall I'm satisfied.",
    "The design is beautiful, but the material feels cheap. Hoping it lasts longer than it looks.",
    "Received the wrong color, but the seller responded quickly and sent a replacement. Happy with the resolution.",
    "There are so many similar products, but this one stands out for its ease of use and thoughtful features."
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
