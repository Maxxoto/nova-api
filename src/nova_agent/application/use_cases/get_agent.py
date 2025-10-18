"""Get agent use case."""

from uuid import UUID

from ...domain.entities import Agent
from ...domain.exceptions import AgentNotFound


class GetAgentUseCase:
    """Use case for getting an agent by ID."""
    
    def __init__(self, agent_repository):
        self.agent_repository = agent_repository
    
    def execute(self, agent_id: UUID) -> Agent:
        """Execute the get agent use case."""
        try:
            return self.agent_repository.get_by_id(agent_id)
        except AgentNotFound:
            raise AgentNotFound(agent_id)