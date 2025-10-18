"""Agent created domain event."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AgentCreated(BaseModel):
    """Domain event emitted when an agent is created."""
    
    agent_id: UUID
    agent_name: str
    created_at: datetime
    capabilities: list[str]
    
    class Config:
        frozen = True  # Events should be immutable