"""Agent configuration value object."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Agent configuration value object."""
    
    model_name: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    system_prompt: Optional[str] = Field(None, max_length=2000)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    def update_parameter(self, key: str, value: Any) -> None:
        """Update a configuration parameter."""
        self.parameters[key] = value
    
    def remove_parameter(self, key: str) -> None:
        """Remove a configuration parameter."""
        if key in self.parameters:
            del self.parameters[key]