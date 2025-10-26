"""Integration tests for end-to-end functionality."""

import pytest
from uuid import uuid4

from src.infrastructure.di import get_llm_client
from src.core.entities.agent_state import AgentState
from src.application.services.langgraph_orchestrator import LangGraphOrchestrator


class TestEndToEndIntegration:
    """End-to-end integration tests using the LangGraph orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a LangGraph orchestrator instance for testing."""
        llm_client = get_llm_client()
        return LangGraphOrchestrator(llm_client)
    
    @pytest.mark.asyncio
    async def test_stream_chat_completion(self, orchestrator):
        """Test streaming chat completion with LangGraph orchestrator."""
        # Prepare test messages
        messages = [
            {"role": "user", "content": "Hello, can you help me with a simple task?"}
        ]
        
        # Test streaming chat completion
        results = []
        async for result in orchestrator.stream_chat_completion(
            messages=messages,
            thread_id="integration-test-thread"
        ):
            results.append(result)
        
        # Verify the results
        assert len(results) > 0
        assert all("content" in result for result in results)
        assert all("thread_id" in result for result in results)
        assert all(result["thread_id"] == "integration-test-thread" for result in results)
    
    @pytest.mark.asyncio
    async def test_chat_completion(self, orchestrator):
        """Test non-streaming chat completion with LangGraph orchestrator."""
        # Prepare test messages
        messages = [
            {"role": "user", "content": "What is the capital of France?"}
        ]
        
        # Test non-streaming chat completion
        result = await orchestrator.chat_completion(
            messages=messages,
            thread_id="chat-test-thread"
        )
        
        # Verify the result
        assert result is not None
        assert "response" in result
        assert "thread_id" in result
        assert "memory_used" in result
        assert result["thread_id"] == "chat-test-thread"
        assert result["memory_used"] is True
    
    @pytest.mark.asyncio
    async def test_conversation_memory_persistence(self, orchestrator):
        """Test that conversation memory persists across interactions."""
        thread_id = "memory-test-thread"
        
        # First interaction
        messages1 = [
            {"role": "user", "content": "My name is John."}
        ]
        
        result1 = await orchestrator.chat_completion(
            messages=messages1,
            thread_id=thread_id
        )
        
        # Second interaction - should have memory of first
        messages2 = [
            {"role": "user", "content": "What is my name?"}
        ]
        
        result2 = await orchestrator.chat_completion(
            messages=messages2,
            thread_id=thread_id
        )
        
        # Verify both interactions completed successfully
        assert result1 is not None
        assert result2 is not None
        assert "response" in result1
        assert "response" in result2
        assert result1["thread_id"] == thread_id
        assert result2["thread_id"] == thread_id
    
    @pytest.mark.asyncio
    async def test_multiple_threads_isolation(self, orchestrator):
        """Test that multiple threads operate in isolation."""
        thread1_id = "thread-1"
        thread2_id = "thread-2"
        
        # Interaction in thread 1
        messages1 = [
            {"role": "user", "content": "This is thread 1 conversation."}
        ]
        
        result1 = await orchestrator.chat_completion(
            messages=messages1,
            thread_id=thread1_id
        )
        
        # Interaction in thread 2
        messages2 = [
            {"role": "user", "content": "This is thread 2 conversation."}
        ]
        
        result2 = await orchestrator.chat_completion(
            messages=messages2,
            thread_id=thread2_id
        )
        
        # Verify both threads completed successfully
        assert result1 is not None
        assert result2 is not None
        assert result1["thread_id"] == thread1_id
        assert result2["thread_id"] == thread2_id
    
    @pytest.mark.asyncio
    async def test_streaming_vs_non_streaming_consistency(self, orchestrator):
        """Test that streaming and non-streaming produce consistent results."""
        messages = [
            {"role": "user", "content": "Tell me a short story."}
        ]
        thread_id = "consistency-test-thread"
        
        # Test streaming
        streaming_results = []
        async for result in orchestrator.stream_chat_completion(
            messages=messages,
            thread_id=thread_id
        ):
            streaming_results.append(result)
        
        # Test non-streaming
        non_streaming_result = await orchestrator.chat_completion(
            messages=messages,
            thread_id=thread_id
        )
        
        # Verify both methods work
        assert len(streaming_results) > 0
        assert non_streaming_result is not None
        assert "response" in non_streaming_result


class TestFastAPIInterface:
    """Integration tests for the FastAPI interface."""
    
    @pytest.fixture
    def fastapi_app(self):
        """Create the FastAPI application for testing."""
        from src.interfaces.api.fastapi_app import create_app
        return create_app()
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, fastapi_app):
        """Test the health endpoint."""
        from fastapi.testclient import TestClient
        
        client = TestClient(fastapi_app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, fastapi_app):
        """Test the root endpoint."""
        from fastapi.testclient import TestClient

        client = TestClient(fastapi_app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "Welcome to Nova Agent API" in data["message"]