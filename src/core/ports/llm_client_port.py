"""LLM Client Port for hexagonal architecture."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional


class LLMClientPort(ABC):
    """Abstract base class for LLM client implementations."""
    
    @abstractmethod
    def invoke(self, messages: List[Any]) -> Any:
        """Invoke the LLM with messages and return response.
        
        Args:
            messages: List of messages to send to LLM
            
        Returns:
            LLM response object
        """
        pass
    
    @abstractmethod
    async def stream_chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion with memory context.
        
        Args:
            messages: List of chat messages
            thread_id: Optional thread ID for conversation context
            
        Yields:
            Dictionary containing content and thread_id
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion with memory context.
        
        Args:
            messages: List of chat messages
            thread_id: Optional thread ID for conversation context
            
        Returns:
            Dictionary containing response, thread_id, and memory status
        """
        pass