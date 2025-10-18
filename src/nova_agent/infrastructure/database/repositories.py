"""Database repositories for Nova Agent API."""

from uuid import UUID

from sqlalchemy.orm import Session

from ....domain.entities import Agent
from ....domain.exceptions import AgentNotFound
from .models import AgentModel


class SQLAgentRepository:
    """SQLAlchemy-based implementation of AgentRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, agent: Agent) -> None:
        """Save an agent to the database."""
        agent_model = AgentModel.from_domain(agent)
        
        # Check if agent exists
        existing_agent = self.session.query(AgentModel).filter(AgentModel.id == agent.id).first()
        
        if existing_agent:
            # Update existing agent
            existing_agent.name = agent.name
            existing_agent.description = agent.description
            existing_agent.capabilities = agent.capabilities
            existing_agent.status = agent.status
            existing_agent.updated_at = agent.updated_at
        else:
            # Add new agent
            self.session.add(agent_model)
        
        self.session.commit()
    
    def get_by_id(self, agent_id: UUID) -> Agent:
        """Get agent by ID from the database."""
        agent_model = self.session.query(AgentModel).filter(AgentModel.id == agent_id).first()
        
        if not agent_model:
            raise AgentNotFound(agent_id)
        
        return agent_model.to_domain()
    
    def get_all(self) -> list[Agent]:
        """Get all agents from the database."""
        agent_models = self.session.query(AgentModel).all()
        return [agent_model.to_domain() for agent_model in agent_models]
    
    def delete(self, agent_id: UUID) -> None:
        """Delete an agent from the database."""
        agent_model = self.session.query(AgentModel).filter(AgentModel.id == agent_id).first()
        
        if not agent_model:
            raise AgentNotFound(agent_id)
        
        self.session.delete(agent_model)
        self.session.commit()