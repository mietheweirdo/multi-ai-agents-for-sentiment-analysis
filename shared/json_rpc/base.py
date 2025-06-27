# shared/json_rpc/base.py
"""
Base JSON-RPC utilities following A2A Cross-Framework POC pattern.
"""

import json
import logging
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

logger = logging.getLogger(__name__)

class JsonRpcRequest(BaseModel):
    """Standard JSON-RPC 2.0 request model"""
    jsonrpc: Literal["2.0"]
    id: str
    method: str
    params: Dict[str, Any]

class JsonRpcResponse(BaseModel):
    """Standard JSON-RPC 2.0 response model"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class A2AArtifact(BaseModel):
    """A2A protocol artifact structure"""
    parts: list
    index: int = 0
    append: bool = False
    lastChunk: bool = True

class A2AResult(BaseModel):
    """A2A protocol result structure"""
    id: Optional[str] = None
    sessionId: Optional[str] = None
    status: Dict[str, str] = {"state": "completed"}
    artifacts: list[A2AArtifact]
    metadata: Dict[str, Any] = {}

def create_a2a_response(
    request_id: str,
    task_id: Optional[str],
    output_text: str,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> JsonRpcResponse:
    """
    Create a standardized A2A-compliant JSON-RPC response.
    
    Args:
        request_id: The JSON-RPC request ID
        task_id: The task ID from params
        output_text: The agent's output text
        session_id: Optional session identifier
        metadata: Optional metadata dictionary
    
    Returns:
        JsonRpcResponse: Formatted A2A response
    """
    artifact = A2AArtifact(
        parts=[
            {
                "type": "text",
                "text": {"raw": output_text}
            }
        ]
    )
    
    result = A2AResult(
        id=task_id,
        sessionId=session_id,
        artifacts=[artifact],
        metadata=metadata or {}
    )
    
    return JsonRpcResponse(
        id=request_id,
        result=result.dict()
    )

def create_error_response(request_id: str, error_code: int, error_message: str) -> JsonRpcResponse:
    """Create a JSON-RPC error response"""
    return JsonRpcResponse(
        id=request_id,
        error={
            "code": error_code,
            "message": error_message
        }
    )

def extract_text_from_message(message: Dict[str, Any]) -> str:
    """
    Extract text content from A2A message parts.
    
    Args:
        message: The message dictionary from JSON-RPC params
        
    Returns:
        str: Extracted text content
        
    Raises:
        ValueError: If no text content found
    """
    parts = message.get("parts", [])
    for part in parts:
        if part.get("type") == "text":
            text_content = part.get("text", "")
            if isinstance(text_content, str):
                return text_content
            elif isinstance(text_content, dict) and "raw" in text_content:
                return text_content["raw"]
    
    raise ValueError("No text content found in message parts")

def setup_agent_card_endpoint(app: FastAPI, card_path: str):
    """Setup the /.well-known/agent.json endpoint"""
    @app.get("/.well-known/agent.json")
    async def agent_card():
        try:
            with open(card_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Agent card not found")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid agent card format")

def validate_rpc_request(rpc_req: JsonRpcRequest) -> Optional[JsonRpcResponse]:
    """
    Validate JSON-RPC request and return error response if invalid.
    
    Returns:
        None if valid, JsonRpcResponse with error if invalid
    """
    if rpc_req.method != "tasks/send":
        return create_error_response(
            rpc_req.id,
            -32601,
            "Method not found"
        )
    
    if "message" not in rpc_req.params:
        return create_error_response(
            rpc_req.id,
            -32602,
            "Missing 'message' parameter"
        )
    
    try:
        extract_text_from_message(rpc_req.params["message"])
    except ValueError as e:
        return create_error_response(
            rpc_req.id,
            -32602,
            f"Invalid message format: {str(e)}"
        )
    
    return None
