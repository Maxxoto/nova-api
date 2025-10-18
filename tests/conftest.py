"""Pytest configuration and fixtures for Nova Agent API tests."""

import pytest
from fastapi.testclient import TestClient

from src.nova_agent.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "capabilities": ["chat", "email"],
        "status": "active"
    }