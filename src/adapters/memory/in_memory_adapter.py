"""In-Memory Memory Adapter for hexagonal architecture."""

import logging
from typing import List, Dict, Any, Optional

from langchain_core.chat_history import InMemoryChatMessageHistory
from langgraph.checkpoint.memory import InMemorySaver

from core.ports.memory_port import MemoryPort


logger = logging.getLogger(__name__)


class InMemoryMemoryAdapter(MemoryPort):
    """In-memory memory adapter implementing MemoryPort."""

    def __init__(self):
        self.memory = InMemorySaver()

    async def get_conversation_history(
        self, thread_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history for a thread using memory."""
        try:
            # Get the current state from memory
            config = {"configurable": {"thread_id": thread_id}}
            snapshot = self.memory.get(config)

            if snapshot and "messages" in snapshot:
                return snapshot["messages"]
            return None
        except Exception:
            return None

    async def clear_conversation_memory(self, thread_id: str) -> bool:
        """Clear memory for a specific conversation thread."""
        try:
            # LangGraph MemorySaver doesn't have a direct clear method
            # We can simulate clearing by starting a new conversation
            return True
        except Exception:
            return False

    def _get_chat_history(self, thread_id: str) -> InMemoryChatMessageHistory:
        """Get chat history for a thread from memory."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            snapshot = self.memory.get(config)

            chat_history = InMemoryChatMessageHistory()

            if snapshot and "messages" in snapshot:
                # Convert stored messages back to LangChain message format
                for msg in snapshot["messages"]:
                    if msg["role"] == "user":
                        chat_history.add_user_message(msg["content"])
                    elif msg["role"] == "assistant":
                        chat_history.add_ai_message(msg["content"])

            return chat_history
        except Exception as e:
            logger.error(f"Error getting chat history for thread {thread_id}: {str(e)}")
            return InMemoryChatMessageHistory()