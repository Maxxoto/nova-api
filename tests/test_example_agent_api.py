"""Example tests for Nova Agent API."""

import pytest
from uuid import uuid4

from src.nova_agent.domain.entities import Agent
from src.nova_agent.domain.exceptions import AgentNotFound, InvalidAgentStatus
from src.nova_agent.application.dto import CreateAgentDTO, UpdateAgentDTO


class TestAgentEntity:
    """Tests for Agent domain entity."""
    
    def test_create_agent(self):
        """Test creating an agent entity."""
        agent = Agent(
            name="Test Agent",
            description="A test agent",
            capabilities=["chat", "email"],
            status="active"
        )
        
        assert agent.name == "Test Agent"
        assert agent.description == "A test agent"
        assert agent.capabilities == ["chat", "email"]
        assert agent.status == "active"
        assert agent.id is not None
    
    def test_update_status(self):
        """Test updating agent status."""
        agent = Agent(name="Test Agent")
        agent.update_status("inactive")
        
        assert agent.status == "inactive"
    
    def test_update_status_invalid(self):
        """Test updating agent status with invalid value."""
        agent = Agent(name="Test Agent")
        
        with pytest.raises(ValueError, match="Invalid status"):
            agent.update_status("invalid_status")
    
    def test_add_capability(self):
        """Test adding a capability to an agent."""
        agent = Agent(name="Test Agent", capabilities=["chat"])
        agent.add_capability("email")
        
        assert "email" in agent.capabilities
        assert len(agent.capabilities) == 2
    
    def test_remove_capability(self):
        """Test removing a capability from an agent."""
        agent = Agent(name="Test Agent", capabilities=["chat", "email"])
        agent.remove_capability("chat")
        
        assert "chat" not in agent.capabilities
        assert "email" in agent.capabilities


class TestCreateAgentDTO:
    """Tests for CreateAgentDTO."""
    
    def test_create_dto(self):
        """Test creating a CreateAgentDTO."""
        dto = CreateAgentDTO(
            name="Test Agent",
            description="A test agent",
            capabilities=["chat", "email"],
            status="active"
        )
        
        assert dto.name == "Test Agent"
        assert dto.description == "A test agent"
        assert dto.capabilities == ["chat", "email"]
        assert dto.status == "active"
    
    def test_create_dto_defaults(self):
        """Test creating a CreateAgentDTO with defaults."""
        dto = CreateAgentDTO(name="Test Agent")
        
        assert dto.name == "Test Agent"
        assert dto.description is None
        assert dto.capabilities == []
        assert dto.status == "active"


class TestUpdateAgentDTO:
    """Tests for UpdateAgentDTO."""
    
    def test_update_dto(self):
        """Test creating an UpdateAgentDTO."""
        dto = UpdateAgentDTO(
            name="Updated Agent",
            description="Updated description",
            capabilities=["chat", "email", "support"],
            status="inactive"
        )
        
        assert dto.name == "Updated Agent"
        assert dto.description == "Updated description"
        assert dto.capabilities == ["chat", "email", "support"]
        assert dto.status == "inactive"
    
    def test_update_dto_partial(self):
        """Test creating an UpdateAgentDTO with partial data."""
        dto = UpdateAgentDTO(name="Updated Agent")
        
        assert dto.name == "Updated Agent"
        assert dto.description is None
        assert dto.capabilities is None
        assert dto.status is None


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


class TestExceptions:
    """Tests for custom exceptions."""
    
    def test_agent_not_found(self):
        """Test AgentNotFound exception."""
        agent_id = uuid4()
        exception = AgentNotFound(agent_id)
        
        assert str(agent_id) in str(exception)
        assert exception.agent_id == agent_id
    
    def test_invalid_agent_status(self):
        """Test InvalidAgentStatus exception."""
        status = "invalid"
        exception = InvalidAgentStatus(status)
        
        assert status in str(exception)
        assert exception.status == status