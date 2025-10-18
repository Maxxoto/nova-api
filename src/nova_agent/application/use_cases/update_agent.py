"""Update agent use case."""

from typing import Optional
from uuid import UUID

from ...domain.entities import Agent
from ...domain.events import AgentUpdated
from ...domain.exceptions import AgentNotFound, InvalidAgentStatus
from ..dto import UpdateAgentDTO
from ..services import EventPublisher


class UpdateAgentUseCase:
    """Use case for updating an agent."""
    
    def __init__(self, agent_repository, event_publisher: EventPublisher):
        self.agent_repository = agent_repository
        self.event_publisher = event_publisher
    
    def execute(self, agent_id: UUID, dto: UpdateAgentDTO) -> Agent:
        """Execute the update agent use case."""
        
        # Get existing agent
        try:
            agent = self.agent_repository.get_by_id(agent_id)
        except AgentNotFound:
            raise AgentNotFound(agent_id)
        
        # Track updated fields
        updated_fields = []
        previous_status = agent.status
        
        # Update fields if provided
        if dto.name is not None:
            agent.name = dto.name
            updated_fields.append("name")
        
        if dto.description is not None:
            agent.description = dto.description
            updated_fields.append("description")
        
        if dto.capabilities is not None:
            agent.capabilities = dto.capabilities
            updated_fields.append("capabilities")
        
        if dto.status is not None:
            if dto.status not in ["active", "inactive", "maintenance"]:
                raise InvalidAgentStatus(dto.status)
            agent.status = dto.status
            updated_fields.append("status")
        
        # Save updated agent
        self.agent_repository.save(agent)
        
        # Publish domain event if any fields were updated
        if updated_fields:
            event = AgentUpdated(
                agent_id=agent.id,
                updated_fields=updated_fields,
                updated_at=agent.updated_at,
                previous_status=previous_status if "status" in updated_fields else None,
                new_status=agent.status if "status" in updated_fields else None,
            )
            self.event_publisher.publish(event)
        
        return agent