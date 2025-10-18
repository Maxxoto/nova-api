"""Database models for Nova Agent API."""

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AgentModel(Base):
    """SQLAlchemy model for Agent entity."""
    
    __tablename__ = "agents"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    capabilities = Column(ARRAY(String), nullable=False, default=[])
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_domain(self):
        """Convert database model to domain entity."""
        from ...domain.entities import Agent
        
        return Agent(
            id=self.id,
            name=self.name,
            description=self.description,
            capabilities=self.capabilities,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
    
    @classmethod
    def from_domain(cls, agent):
        """Create database model from domain entity."""
        return cls(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            capabilities=agent.capabilities,
            status=agent.status,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )