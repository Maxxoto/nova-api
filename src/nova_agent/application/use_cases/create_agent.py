"""Create agent use case."""

from typing import Protocol
from uuid import UUID

from ...domain.entities import Agent
from ...domain.events import AgentCreated
from ...domain.exceptions import InvalidAgentStatus
from ..dto import CreateAgentDTO
from ..services import EventPublisher


class AgentRepository(Protocol):
    """Protocol defining agent repository interface."""
    
    def save(self, agent: Agent) -> None:
        """Save an agent."""
        ...
    
    def get_by_id(self, agent_id: UUID) -> Agent:
        """Get agent by ID."""
        ...


class CreateAgentUseCase:
    """Use case for creating a new agent."""
    
    def __init__(self, agent_repository: AgentRepository, event_publisher: EventPublisher):
        self.agent_repository = agent_repository
        self.event_publisher = event_publisher
    
    def execute(self, dto: CreateAgentDTO) -> Agent:
        """Execute the create agent use case."""
        
        # Validate status
        if dto.status not in ["active", "inactive", "maintenance"]:
            raise InvalidAgentStatus(dto.status)
        
        # Create agent entity
        agent = Agent(
            name=dto.name,
            description=dto.description,
            capabilities=dto.capabilities,
            status=dto.status,
        )
        
        # Save agent
        self.agent_repository.save(agent)
        
        # Publish domain event
        event = AgentCreated(
            agent_id=agent.id,
            agent_name=agent.name,
            created_at=agent.created_at,
            capabilities=agent.capabilities,
        )
        self.event_publisher.publish(event)
        
        return agent