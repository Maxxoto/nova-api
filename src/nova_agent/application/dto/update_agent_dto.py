"""Update Agent Data Transfer Object."""

from typing import Optional

from pydantic import BaseModel, Field


class UpdateAgentDTO(BaseModel):
    """DTO for updating an existing agent."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Agent name")
    description: Optional[str] = Field(None, max_length=500, description="Agent description")
    capabilities: Optional[list[str]] = Field(None, description="Agent capabilities")
    status: Optional[str] = Field(None, description="Agent status")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Enhanced Customer Support Agent",
                "description": "Handles customer inquiries with advanced capabilities",
                "capabilities": ["chat", "email", "ticket_management", "faq_generation"],
                "status": "active"
            }
        }