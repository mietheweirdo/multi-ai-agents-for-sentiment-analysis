# tests/test_rpc_endpoints.py
"""
Test suite for A2A JSON-RPC endpoints
Tests individual agents and coordinator following A2A Cross-Framework POC patterns
"""

import pytest
import json
import uuid
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Test data
SAMPLE_REVIEW_TEXT = "This smartphone is amazing! Great camera quality and battery life. However, delivery was slow and customer service could be better."

SAMPLE_METADATA = {
    "product_category": "electronics",
    "max_tokens": 150
}

def create_test_payload(text: str = SAMPLE_REVIEW_TEXT, metadata: dict = None) -> dict:
    """Create a test JSON-RPC payload"""
    task_id = str(uuid.uuid4())
    return {
        "jsonrpc": "2.0",
        "id": task_id,
        "method": "tasks/send",
        "params": {
            "id": task_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": text}]
            },
            "metadata": metadata or SAMPLE_METADATA
        }
    }

def validate_a2a_response(response: dict) -> bool:
    """Validate A2A-compliant JSON-RPC response structure"""
    required_fields = ["jsonrpc", "id"]
    
    for field in required_fields:
        if field not in response:
            return False
    
    if response["jsonrpc"] != "2.0":
        return False
    
    if "result" in response:
        result = response["result"]
        if "artifacts" not in result:
            return False
        
        artifacts = result["artifacts"]
        if not isinstance(artifacts, list) or len(artifacts) == 0:
            return False
        
        artifact = artifacts[0]
        if "parts" not in artifact:
            return False
        
        parts = artifact["parts"]
        if not isinstance(parts, list) or len(parts) == 0:
            return False
        
        part = parts[0]
        if "type" not in part or part["type"] != "text":
            return False
        
        if "text" not in part or "raw" not in part["text"]:
            return False
    
    return True

class TestQualityAgentRPC:
    """Test Quality Agent RPC endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        from rpc_servers.quality_agent_rpc import app
        self.client = TestClient(app)
    
    def test_agent_card_endpoint(self):
        """Test /.well-known/agent.json endpoint"""
        response = self.client.get("/.well-known/agent.json")
        assert response.status_code == 200
        
        card = response.json()
        assert card["name"] == "Product Quality Sentiment Agent"
        assert card["agent_type"] == "quality"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        health = response.json()
        assert health["status"] == "healthy"
        assert health["agent"] == "quality"
    
    @patch('rpc_servers.quality_agent_rpc.ProductQualityAgent')
    def test_rpc_endpoint_success(self, mock_agent_class):
        """Test successful RPC call"""
        # Mock agent response
        mock_agent = Mock()
        mock_agent.analyze.return_value = {
            "sentiment": "positive",
            "confidence": 0.85,
            "emotions": ["satisfied", "impressed"],
            "topics": ["camera", "battery"],
            "reasoning": "Excellent product quality",
            "business_impact": "High customer satisfaction"
        }
        mock_agent_class.return_value = mock_agent
        
        payload = create_test_payload()
        response = self.client.post("/rpc", json=payload)
        
        assert response.status_code == 200
        
        result = response.json()
        assert validate_a2a_response(result)
        
        # Verify agent was called
        mock_agent.analyze.assert_called_once_with(SAMPLE_REVIEW_TEXT)
    
    def test_rpc_endpoint_invalid_method(self):
        """Test RPC call with invalid method"""
        payload = create_test_payload()
        payload["method"] = "invalid/method"
        
        response = self.client.post("/rpc", json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == -32601
    
    def test_rpc_endpoint_missing_text(self):
        """Test RPC call with missing text content"""
        payload = create_test_payload()
        payload["params"]["message"]["parts"] = [{"type": "image", "data": "base64"}]
        
        response = self.client.post("/rpc", json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "error" in result
        assert result["error"]["code"] == -32602

class TestExperienceAgentRPC:
    """Test Customer Experience Agent RPC endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        from rpc_servers.experience_agent_rpc import app
        self.client = TestClient(app)
    
    def test_agent_card_endpoint(self):
        """Test /.well-known/agent.json endpoint"""
        response = self.client.get("/.well-known/agent.json")
        assert response.status_code == 200
        
        card = response.json()
        assert card["name"] == "Customer Experience Sentiment Agent"
        assert card["agent_type"] == "experience"
    
    @patch('rpc_servers.experience_agent_rpc.CustomerExperienceAgent')
    def test_rpc_endpoint_success(self, mock_agent_class):
        """Test successful RPC call"""
        mock_agent = Mock()
        mock_agent.analyze.return_value = {
            "sentiment": "negative",
            "confidence": 0.75,
            "emotions": ["frustrated", "disappointed"],
            "topics": ["delivery", "customer service"],
            "reasoning": "Poor delivery and service experience",
            "business_impact": "Customer retention risk"
        }
        mock_agent_class.return_value = mock_agent
        
        payload = create_test_payload()
        response = self.client.post("/rpc", json=payload)
        
        assert response.status_code == 200
        
        result = response.json()
        assert validate_a2a_response(result)

class TestCoordinatorAgentRPC:
    """Test Coordinator Agent RPC endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        from rpc_servers.coordinator_agent_rpc import app
        self.client = TestClient(app)
    
    def test_agent_card_endpoint(self):
        """Test /.well-known/agent.json endpoint"""
        response = self.client.get("/.well-known/agent.json")
        assert response.status_code == 200
        
        card = response.json()
        assert card["name"] == "Multi-Agent Sentiment Coordinator"
        assert card["agent_type"] == "coordinator"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        health = response.json()
        assert health["status"] == "healthy"
        assert health["agent"] == "coordinator"
        assert "available_categories" in health
        assert "available_agent_types" in health
    
    def test_config_endpoint(self):
        """Test configuration endpoint"""
        response = self.client.get("/config")
        assert response.status_code == 200
        
        config = response.json()
        # Should show not initialized initially
        assert config.get("status") == "not_initialized" or "product_category" in config
    
    @patch('rpc_servers.coordinator_agent_rpc.EnhancedCoordinatorAgent')
    def test_rpc_endpoint_success(self, mock_coordinator_class):
        """Test successful coordinated analysis"""
        # Mock coordinator response
        mock_coordinator = Mock()
        mock_coordinator.product_category = "electronics"
        mock_coordinator.sentiment_agents = [Mock(), Mock(), Mock(), Mock()]  # 4 agents
        mock_coordinator.max_tokens_per_agent = 150
        mock_coordinator.run_workflow.return_value = {
            "product_id": "test",
            "product_category": "electronics",
            "review_text": SAMPLE_REVIEW_TEXT,
            "agent_analyses": [
                {
                    "agent_type": "quality",
                    "sentiment": "positive",
                    "confidence": 0.85,
                    "emotions": ["satisfied"],
                    "topics": ["camera", "battery"],
                    "reasoning": "Good quality",
                    "business_impact": "Positive"
                },
                {
                    "agent_type": "experience",
                    "sentiment": "negative", 
                    "confidence": 0.75,
                    "emotions": ["frustrated"],
                    "topics": ["delivery", "service"],
                    "reasoning": "Poor service",
                    "business_impact": "Risk"
                }
            ],
            "consensus": {
                "overall_sentiment": "mixed",
                "overall_confidence": 0.80,
                "agreement_level": "moderate",
                "key_insights": "Mixed feedback on product vs service",
                "business_recommendations": "Improve delivery and service"
            },
            "analysis_metadata": {
                "total_agents": 4,
                "discussion_rounds": 2,
                "average_confidence": 0.80
            }
        }
        mock_coordinator_class.return_value = mock_coordinator
        
        payload = create_test_payload()
        payload["params"]["metadata"]["agent_types"] = ["quality", "experience", "user_experience", "business"]
        
        response = self.client.post("/rpc", json=payload)
        
        assert response.status_code == 200
        
        result = response.json()
        assert validate_a2a_response(result)
        
        # Verify coordinator was called
        mock_coordinator.run_workflow.assert_called_once()

class TestEndToEndWorkflow:
    """Test end-to-end workflow scenarios"""
    
    @patch('requests.post')
    def test_sequential_agent_chain(self, mock_post):
        """Test sequential chain of agent calls"""
        # Mock responses for different agents
        quality_response = {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {
                "artifacts": [
                    {
                        "parts": [
                            {
                                "type": "text",
                                "text": {
                                    "raw": json.dumps({
                                        "sentiment": "positive",
                                        "confidence": 0.85,
                                        "emotions": ["satisfied"],
                                        "topics": ["quality"],
                                        "reasoning": "Good quality",
                                        "business_impact": "Positive"
                                    })
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        experience_response = {
            "jsonrpc": "2.0", 
            "id": "test-id",
            "result": {
                "artifacts": [
                    {
                        "parts": [
                            {
                                "type": "text",
                                "text": {
                                    "raw": json.dumps({
                                        "sentiment": "negative",
                                        "confidence": 0.75,
                                        "emotions": ["frustrated"],
                                        "topics": ["delivery"],
                                        "reasoning": "Poor delivery",
                                        "business_impact": "Risk"
                                    })
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        # Mock requests to return different responses
        mock_post.side_effect = [
            Mock(json=lambda: quality_response, status_code=200),
            Mock(json=lambda: experience_response, status_code=200)
        ]
        
        # Simulate calling quality agent, then experience agent
        from app import call_agent_rpc, extract_result_text, parse_agent_result
        
        # Call quality agent
        quality_result_raw = call_agent_rpc("http://localhost:8001/rpc", SAMPLE_REVIEW_TEXT)
        quality_text = extract_result_text(quality_result_raw)
        quality_result = parse_agent_result(quality_text)
        
        assert quality_result["sentiment"] == "positive"
        assert quality_result["confidence"] == 0.85
        
        # Call experience agent
        experience_result_raw = call_agent_rpc("http://localhost:8002/rpc", SAMPLE_REVIEW_TEXT)
        experience_text = extract_result_text(experience_result_raw)
        experience_result = parse_agent_result(experience_text)
        
        assert experience_result["sentiment"] == "negative"
        assert experience_result["confidence"] == 0.75
        
        # Verify both agents were called
        assert mock_post.call_count == 2

def test_json_rpc_base_utilities():
    """Test shared JSON-RPC utilities"""
    from shared.json_rpc.base import (
        create_a2a_response, 
        create_error_response,
        extract_text_from_message,
        validate_rpc_request,
        JsonRpcRequest
    )
    
    # Test A2A response creation
    response = create_a2a_response(
        request_id="test-123",
        task_id="task-456", 
        output_text="Test output",
        metadata={"test": "value"}
    )
    
    assert response.jsonrpc == "2.0"
    assert response.id == "test-123"
    assert response.result["id"] == "task-456"
    assert response.result["artifacts"][0]["parts"][0]["text"]["raw"] == "Test output"
    
    # Test error response creation
    error_response = create_error_response("test-123", -32601, "Method not found")
    assert error_response.error["code"] == -32601
    assert error_response.error["message"] == "Method not found"
    
    # Test text extraction
    message = {
        "parts": [
            {"type": "text", "text": "Sample text"},
            {"type": "image", "data": "base64"}
        ]
    }
    extracted = extract_text_from_message(message)
    assert extracted == "Sample text"
    
    # Test request validation
    valid_request = JsonRpcRequest(
        jsonrpc="2.0",
        id="test-123",
        method="tasks/send",
        params={
            "message": {
                "parts": [{"type": "text", "text": "test"}]
            }
        }
    )
    
    validation_result = validate_rpc_request(valid_request)
    assert validation_result is None  # No error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
