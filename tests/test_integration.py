# tests/test_integration.py
"""
Integration tests for the complete A2A multi-agent sentiment analysis system
Tests end-to-end workflows and agent coordination
"""

import pytest
import json
import uuid
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Test scenarios
INTEGRATION_TEST_SCENARIOS = [
    {
        "name": "positive_electronics_review",
        "review": "This smartphone is absolutely fantastic! The camera quality is outstanding, battery life lasts all day, and the build quality feels premium. Fast delivery and excellent customer service.",
        "product_category": "electronics",
        "expected_overall_sentiment": "positive",
        "expected_agent_count": 4
    },
    {
        "name": "mixed_fashion_review", 
        "review": "I love the style and fabric of this dress! The fit is perfect and it looks exactly like the photos. However, the delivery took much longer than expected and the packaging was damaged.",
        "product_category": "fashion",
        "expected_overall_sentiment": "mixed",
        "expected_agent_count": 4
    },
    {
        "name": "negative_service_review",
        "review": "The product quality is okay, but the customer service was terrible. They were unresponsive to my questions and the delivery was delayed by a week without any notification.",
        "product_category": "electronics",
        "expected_overall_sentiment": "negative",
        "expected_agent_count": 4
    }
]

class TestMultiAgentCoordination:
    """Test multi-agent coordination and consensus building"""
    
    @patch('agents.enhanced_coordinator.EnhancedCoordinatorAgent')
    def test_coordinator_workflow_integration(self, mock_coordinator_class):
        """Test complete coordinator workflow integration"""
        
        # Mock individual agent responses
        mock_agent_responses = [
            {
                "agent_type": "quality",
                "sentiment": "positive",
                "confidence": 0.85,
                "emotions": ["satisfied", "impressed"],
                "topics": ["build quality", "camera"],
                "reasoning": "Excellent product quality and features",
                "business_impact": "Strong customer satisfaction"
            },
            {
                "agent_type": "experience", 
                "sentiment": "positive",
                "confidence": 0.90,
                "emotions": ["pleased", "satisfied"],
                "topics": ["delivery", "customer service"],
                "reasoning": "Fast delivery and excellent service",
                "business_impact": "Positive customer experience"
            },
            {
                "agent_type": "user_experience",
                "sentiment": "positive",
                "confidence": 0.88,
                "emotions": ["delighted", "happy"],
                "topics": ["usability", "design"],
                "reasoning": "User-friendly design and great experience",
                "business_impact": "High user satisfaction"
            },
            {
                "agent_type": "business",
                "sentiment": "positive", 
                "confidence": 0.82,
                "emotions": ["confident"],
                "topics": ["market position", "value"],
                "reasoning": "Strong market position and value proposition",
                "business_impact": "Competitive advantage"
            }
        ]
        
        # Mock coordinator workflow result
        mock_workflow_result = {
            "product_id": "test_product",
            "product_category": "electronics",
            "review_text": INTEGRATION_TEST_SCENARIOS[0]["review"],
            "agent_analyses": mock_agent_responses,
            "consensus": {
                "overall_sentiment": "positive",
                "overall_confidence": 0.86,
                "agreement_level": "high",
                "key_insights": "Unanimously positive sentiment across all aspects - product quality, service, user experience, and business value",
                "business_recommendations": "Continue current practices and leverage positive feedback for marketing. Focus on maintaining quality standards and service excellence."
            },
            "analysis_metadata": {
                "total_agents": 4,
                "discussion_rounds": 2,
                "average_confidence": 0.86,
                "agreement_score": 0.95,
                "analysis_duration": 2.5,
                "product_category": "electronics"
            }
        }
        
        # Setup mock coordinator
        mock_coordinator = Mock()
        mock_coordinator.product_category = "electronics"
        mock_coordinator.sentiment_agents = [Mock() for _ in range(4)]
        mock_coordinator.max_tokens_per_agent = 150
        mock_coordinator.run_workflow.return_value = mock_workflow_result
        mock_coordinator_class.return_value = mock_coordinator
        
        # Test coordinator creation and execution
        from rpc_servers.coordinator_agent_rpc import create_coordinator
        
        coordinator = create_coordinator(
            product_category="electronics",
            agent_types=["quality", "experience", "user_experience", "business"],
            max_tokens_per_agent=150,
            max_tokens_consensus=800
        )
        
        result = coordinator.run_workflow(
            reviews=[INTEGRATION_TEST_SCENARIOS[0]["review"]],
            product_category="electronics"
        )
        
        # Validate result structure
        assert "consensus" in result
        assert "agent_analyses" in result
        assert "analysis_metadata" in result
        
        # Validate consensus
        consensus = result["consensus"]
        assert consensus["overall_sentiment"] == "positive"
        assert consensus["overall_confidence"] > 0.8
        assert "key_insights" in consensus
        assert "business_recommendations" in consensus
        
        # Validate agent analyses
        agent_analyses = result["agent_analyses"]
        assert len(agent_analyses) == 4
        
        for analysis in agent_analyses:
            assert "agent_type" in analysis
            assert "sentiment" in analysis
            assert "confidence" in analysis
            assert "reasoning" in analysis
            assert "business_impact" in analysis
        
        # Validate metadata
        metadata = result["analysis_metadata"]
        assert metadata["total_agents"] == 4
        assert "discussion_rounds" in metadata
        assert "average_confidence" in metadata

class TestAgentSpecialization:
    """Test that agents maintain their specialization and focus areas"""
    
    def test_quality_agent_specialization(self):
        """Test that quality agent focuses on quality-related aspects"""
        from agents.sentiment_agents import ProductQualityAgent
        
        config = {
            "api_key": "test_key",
            "model_name": "gpt-4o-mini"
        }
        
        with patch('agents.sentiment_agents.ChatOpenAI') as mock_llm:
            # Mock LLM response for quality analysis
            mock_chain = Mock()
            mock_chain.invoke.return_value = {
                "sentiment": "positive",
                "confidence": 0.85,
                "emotions": ["satisfied", "impressed"],
                "topics": ["build quality", "durability", "materials"],
                "reasoning": "Excellent build quality and premium materials",
                "business_impact": "Strong quality perception"
            }
            
            with patch.object(ProductQualityAgent, 'chain', mock_chain):
                agent = ProductQualityAgent(config, max_tokens=150, product_category="electronics")
                result = agent.analyze("The phone has excellent build quality and feels very durable.")
                
                # Verify quality-focused analysis
                assert result["sentiment"] == "positive"
                assert "build quality" in result["topics"] or "durability" in result["topics"]
                assert result["agent_type"] == "quality"
    
    def test_experience_agent_specialization(self):
        """Test that experience agent focuses on service-related aspects"""
        from agents.sentiment_agents import CustomerExperienceAgent
        
        config = {
            "api_key": "test_key", 
            "model_name": "gpt-4o-mini"
        }
        
        with patch('agents.sentiment_agents.ChatOpenAI') as mock_llm:
            # Mock LLM response for experience analysis
            mock_chain = Mock()
            mock_chain.invoke.return_value = {
                "sentiment": "negative",
                "confidence": 0.80,
                "emotions": ["frustrated", "disappointed"],
                "topics": ["delivery", "customer service", "communication"],
                "reasoning": "Poor delivery experience and unresponsive service",
                "business_impact": "Customer retention risk"
            }
            
            with patch.object(CustomerExperienceAgent, 'chain', mock_chain):
                agent = CustomerExperienceAgent(config, max_tokens=150, product_category="electronics")
                result = agent.analyze("Delivery was delayed and customer service didn't respond to my emails.")
                
                # Verify service-focused analysis
                assert result["sentiment"] == "negative"
                assert any(topic in ["delivery", "customer service", "communication"] for topic in result["topics"])
                assert result["agent_type"] == "experience"

class TestProductCategorySpecialization:
    """Test product category-specific prompt customization"""
    
    def test_electronics_category_customization(self):
        """Test electronics-specific analysis focus"""
        from agents.prompts import ProductPrompts
        
        # Test product category customization
        available_categories = ProductPrompts.get_available_categories()
        assert "electronics" in available_categories
        
        # Test category-specific focus areas
        electronics_focus = ProductPrompts.get_category_focus("electronics")
        assert any("technical" in focus.lower() or "performance" in focus.lower() for focus in electronics_focus)
        assert any("battery" in focus.lower() for focus in electronics_focus)
    
    def test_fashion_category_customization(self):
        """Test fashion-specific analysis focus"""
        from agents.prompts import ProductPrompts
        
        available_categories = ProductPrompts.get_available_categories()
        assert "fashion" in available_categories
        
        # Test fashion-specific focus areas
        fashion_focus = ProductPrompts.get_category_focus("fashion")
        assert any("fabric" in focus.lower() or "fit" in focus.lower() for focus in fashion_focus)
        assert any("style" in focus.lower() for focus in fashion_focus)

class TestA2AProtocolCompliance:
    """Test A2A protocol compliance across all endpoints"""
    
    def test_agent_card_compliance(self):
        """Test that all agent cards follow A2A specification"""
        import os
        import json
        
        card_dir = os.path.join(os.path.dirname(__file__), "..", "shared", "agent_cards")
        
        # Required fields for A2A agent cards
        required_fields = ["name", "description", "version", "capabilities", "skills"]
        
        # Test all agent cards
        card_files = [
            "quality_agent_card.json",
            "experience_agent_card.json", 
            "user_experience_agent_card.json",
            "business_agent_card.json",
            "technical_agent_card.json",
            "coordinator_agent_card.json"
        ]
        
        for card_file in card_files:
            card_path = os.path.join(card_dir, card_file)
            
            if os.path.exists(card_path):
                with open(card_path, 'r') as f:
                    card = json.load(f)
                
                # Validate required fields
                for field in required_fields:
                    assert field in card, f"Missing required field '{field}' in {card_file}"
                
                # Validate capabilities
                assert isinstance(card["capabilities"], list)
                assert "requestResponse" in card["capabilities"]
                
                # Validate skills
                assert isinstance(card["skills"], list)
                assert len(card["skills"]) > 0
                
                for skill in card["skills"]:
                    assert "name" in skill
                    assert "description" in skill
    
    def test_json_rpc_response_compliance(self):
        """Test JSON-RPC 2.0 response compliance"""
        from shared.json_rpc.base import create_a2a_response
        
        response = create_a2a_response(
            request_id="test-123",
            task_id="task-456",
            output_text="Test analysis result",
            metadata={"agent": "test"}
        )
        
        # Validate JSON-RPC 2.0 compliance
        response_dict = response.dict()
        assert response_dict["jsonrpc"] == "2.0"
        assert response_dict["id"] == "test-123"
        assert "result" in response_dict
        
        # Validate A2A artifact structure
        result = response_dict["result"]
        assert "artifacts" in result
        assert isinstance(result["artifacts"], list)
        assert len(result["artifacts"]) > 0
        
        artifact = result["artifacts"][0]
        assert "parts" in artifact
        assert isinstance(artifact["parts"], list)
        assert len(artifact["parts"]) > 0
        
        part = artifact["parts"][0]
        assert part["type"] == "text"
        assert "text" in part
        assert "raw" in part["text"]
        assert part["text"]["raw"] == "Test analysis result"

class TestErrorHandling:
    """Test error handling across the system"""
    
    def test_invalid_product_category(self):
        """Test handling of invalid product categories"""
        from agents.enhanced_coordinator import EnhancedCoordinatorAgent
        
        config = {"api_key": "test_key", "model_name": "gpt-4o-mini"}
        
        # Test invalid product category
        with pytest.raises(ValueError, match="Unknown product category"):
            coordinator = EnhancedCoordinatorAgent(config=config, product_category="invalid_category")
    
    def test_agent_analysis_failure(self):
        """Test graceful handling of agent analysis failures"""
        from agents.sentiment_agents import ProductQualityAgent
        
        config = {"api_key": "test_key", "model_name": "gpt-4o-mini"}
        
        with patch('agents.sentiment_agents.ChatOpenAI') as mock_llm:
            # Mock LLM to raise an exception
            mock_chain = Mock()
            mock_chain.invoke.side_effect = Exception("API Error")
            
            with patch.object(ProductQualityAgent, 'chain', mock_chain):
                agent = ProductQualityAgent(config, max_tokens=150, product_category="electronics")
                result = agent.analyze("Test review")
                
                # Should return error result with neutral sentiment
                assert result["sentiment"] == "neutral"
                assert result["confidence"] == 0.5
                assert "error" in result["reasoning"]
    
    def test_rpc_error_responses(self):
        """Test RPC error response generation"""
        from shared.json_rpc.base import create_error_response
        
        error_response = create_error_response("test-123", -32601, "Method not found")
        
        response_dict = error_response.dict()
        assert response_dict["jsonrpc"] == "2.0"
        assert response_dict["id"] == "test-123"
        assert "error" in response_dict
        assert response_dict["error"]["code"] == -32601
        assert response_dict["error"]["message"] == "Method not found"

class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior"""
    
    def test_token_limit_compliance(self):
        """Test that agents respect token limits"""
        from agents.sentiment_agents import ProductQualityAgent
        
        config = {"api_key": "test_key", "model_name": "gpt-4o-mini"}
        
        with patch('agents.sentiment_agents.ChatOpenAI') as mock_llm_class:
            mock_llm = Mock()
            mock_llm_class.return_value = mock_llm
            
            # Test different token limits
            for max_tokens in [50, 150, 300]:
                agent = ProductQualityAgent(config, max_tokens=max_tokens, product_category="electronics")
                
                # Verify LLM was initialized with correct token limit
                mock_llm_class.assert_called_with(
                    model="gpt-4o-mini",
                    api_key="test_key",
                    max_tokens=max_tokens,
                    temperature=0.1
                )
    
    def test_concurrent_agent_execution(self):
        """Test that multiple agents can execute concurrently"""
        from agents.sentiment_agents import SentimentAgentFactory
        
        config = {"api_key": "test_key", "model_name": "gpt-4o-mini"}
        
        with patch('agents.sentiment_agents.ChatOpenAI'):
            # Create multiple agents
            agents = SentimentAgentFactory.create_agent_team(
                config=config,
                agent_types=["quality", "experience", "user_experience", "business"],
                max_tokens=150,
                product_category="electronics"
            )
            
            assert len(agents) == 4
            
            # Verify each agent has correct type
            agent_types = [agent.agent_type for agent in agents]
            expected_types = ["quality", "experience", "user_experience", "business"]
            assert set(agent_types) == set(expected_types)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
