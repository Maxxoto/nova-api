"""Create Agent Data Transfer Object."""

from typing import Optional

from pydantic import BaseModel, Field


class CreateAgentDTO(BaseModel):
    """DTO for creating a new agent."""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: Optional[str] = Field(
        None, max_length=500, description="Agent description"
    )
    capabilities: list[str] = Field(
        default_factory=list, description="Agent capabilities"
    )
    status: str = Field(default="active", description="Agent status")

    class Config:
        schema_extra = {
            "example": {
                "name": "Customer Support Agent",
                "description": "Handles customer inquiries and support tickets",
                "capabilities": ["chat", "email", "ticket_management"],
                "status": "active",
            }
        }
