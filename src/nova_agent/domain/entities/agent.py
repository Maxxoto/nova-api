"""Agent domain entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Agent(BaseModel):
    """Agent domain entity representing an AI agent."""
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    capabilities: list[str] = Field(default_factory=list)
    status: str = Field(default="active", regex="^(active|inactive|maintenance)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update_status(self, new_status: str) -> None:
        """Update agent status and timestamp."""
        if new_status not in ["active", "inactive", "maintenance"]:
            raise ValueError("Invalid status")
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = datetime.utcnow()
    
    def remove_capability(self, capability: str) -> None:
        """Remove a capability from the agent."""
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.updated_at = datetime.utcnow()