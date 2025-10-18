"""Agent updated domain event."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AgentUpdated(BaseModel):
    """Domain event emitted when an agent is updated."""
    
    agent_id: UUID
    updated_fields: list[str]
    updated_at: datetime
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    
    class Config:
        frozen = True  # Events should be immutable