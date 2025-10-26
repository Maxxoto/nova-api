"""Chat Service for hexagonal architecture."""

from typing import AsyncGenerator, Dict, Any, List, Optional

from application.services.langgraph_orchestrator import LangGraphOrchestrator
from core.ports.llm_client_port import LLMClientPort
from core.ports.memory_port import MemoryPort


class ChatService:
    """Chat service orchestrating LLM and memory interactions."""
    
    def __init__(self, llm_client: LLMClientPort, memory: MemoryPort):
        self.llm_client = llm_client
        self.memory = memory
        self.orchestrator = LangGraphOrchestrator(llm_client)
    
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
        async for chunk in self.orchestrator.stream_chat_completion(messages, thread_id):
            yield chunk
    
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
        return await self.orchestrator.chat_completion(messages, thread_id)
    
    async def get_conversation_history(
        self, thread_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history for a thread.
        
        Args:
            thread_id: Thread ID for conversation context
            
        Returns:
            List of conversation messages or None if not found
        """
        return await self.memory.get_conversation_history(thread_id)
    
    async def clear_conversation_memory(self, thread_id: str) -> bool:
        """Clear memory for a specific conversation thread.
        
        Args:
            thread_id: Thread ID to clear
            
        Returns:
            True if successful, False otherwise
        """
        return await self.memory.clear_conversation_memory(thread_id)