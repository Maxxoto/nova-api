"""Memory Port for hexagonal architecture."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class MemoryPort(ABC):
    """Abstract base class for memory implementations."""
    
    @abstractmethod
    async def get_conversation_history(
        self, thread_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history for a thread.
        
        Args:
            thread_id: Thread ID for conversation context
            
        Returns:
            List of conversation messages or None if not found
        """
        pass
    
    @abstractmethod
    async def clear_conversation_memory(self, thread_id: str) -> bool:
        """Clear memory for a specific conversation thread.
        
        Args:
            thread_id: Thread ID to clear
            
        Returns:
            True if successful, False otherwise
        """
        pass