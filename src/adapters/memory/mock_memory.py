"""Mock memory adapter for testing and development."""

from typing import List, Optional, Dict, Any
from uuid import UUID

from ...core.entities.agent_state import AgentState
from ...core.ports.memory_port import MemoryPort


class MockMemoryAdapter(MemoryPort):
    """Mock memory adapter for testing."""
    
    def __init__(self):
        self.conversations = {}
        self.agent_states = {}
    
    async def store_conversation(self, thread_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Store conversation messages for a thread."""
        
        if thread_id not in self.conversations:
            self.conversations[thread_id] = []
        
        self.conversations[thread_id].extend(messages)
        return True
    
    async def get_conversation_history(self, thread_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history for a thread."""
        
        return self.conversations.get(thread_id, [])
    
    async def clear_conversation_memory(self, thread_id: str) -> bool:
        """Clear memory for a specific conversation thread."""
        
        if thread_id in self.conversations:
            del self.conversations[thread_id]
            return True
        return False
    
    async def store_agent_state(self, agent_state: AgentState) -> bool:
        """Store agent state."""
        
        self.agent_states[agent_state.id] = agent_state
        return True
    
    async def get_agent_state(self, agent_id: UUID) -> Optional[AgentState]:
        """Get agent state by ID."""
        
        return self.agent_states.get(agent_id)
    
    async def update_agent_state(self, agent_id: UUID, updates: Dict[str, Any]) -> Optional[AgentState]:
        """Update agent state."""
        
        if agent_id in self.agent_states:
            agent_state = self.agent_states[agent_id]
            
            for key, value in updates.items():
                if hasattr(agent_state, key):
                    setattr(agent_state, key, value)
            
            return agent_state
        return None
    
    async def list_agent_states(self) -> List[AgentState]:
        """List all agent states (mock extension)."""
        
        return list(self.agent_states.values())