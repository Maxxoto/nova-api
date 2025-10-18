"""Agent not found exception."""

from uuid import UUID


class AgentNotFound(Exception):
    """Exception raised when an agent is not found."""
    
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        super().__init__(f"Agent with ID {agent_id} not found")