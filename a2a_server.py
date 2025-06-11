# a2a_server.py
"""
A2A protocol server for multi-agent sentiment analysis system.
Exposes CoordinatorAgent via A2A-compliant HTTP endpoint.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from agents.coordinator import CoordinatorAgent
import uuid
import json
import os

# --- A2A Message/Task/Artifact/Part stubs (simplified for demo) ---
# In production, use the a2a SDK types directly if available

def make_text_part(text):
    return {"type": "text", "text": text}

def make_message(role, text):
    return {"role": role, "parts": [make_text_part(text)]}

def make_task_result(task_id, result):
    return {
        "jsonrpc": "2.0",
        "id": task_id,
        "result": {
            "message": make_message("assistant", result),
            "state": "completed"
        }
    }

# --- FastAPI app as A2A endpoint ---
app = FastAPI()

# Load config.json at startup
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

coordinator = CoordinatorAgent()

@app.post("/tasks/send")
async def a2a_task_send(request: Request):
    body = await request.json()
    task_id = body.get("id") or str(uuid.uuid4())
    params = body.get("params", {})
    message = params.get("message", {})
    # Extract product_id or review text from message
    product_id = None
    text = None
    for part in message.get("parts", []):
        if part.get("type") == "text":
            text = part.get("text")
    # For demo: treat text as product_id or review
    result = coordinator.run_workflow(product_id=text)
    return JSONResponse(make_task_result(task_id, result))

@app.get("/.well-known/agent.json")
def agent_card():
    # Minimal AgentCard for A2A discovery
    return {
        "id": "multi-ai-sentiment-agent",
        "name": "Multi-AI Sentiment Analysis Agent",
        "description": "Performs multi-agent sentiment analysis workflow via A2A.",
        "capabilities": ["sentiment-analysis", "reporting"],
        "a2aVersion": "0.4.0"
    }

@app.get("/charts/sentiment_chart.png")
def get_sentiment_chart():
    chart_path = os.path.join(os.path.dirname(__file__), "charts", "sentiment_chart.png")
    if os.path.exists(chart_path):
        return FileResponse(chart_path, media_type="image/png")
    return JSONResponse({"error": "Chart not found"}, status_code=404)
