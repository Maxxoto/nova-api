"""Dependency Injection for hexagonal architecture."""

from fastapi import Depends

from core.ports.llm_client_port import LLMClientPort
from core.ports.memory_port import MemoryPort
from application.services.chat_service import ChatService
from adapters.llm_providers.groq_llm_adapter import GroqLLMAdapter
from adapters.memory.in_memory_adapter import InMemoryMemoryAdapter


# Create singleton instances
_llm_client: LLMClientPort = None
_memory: MemoryPort = None
_chat_service: ChatService = None


def get_llm_client() -> LLMClientPort:
    """Get LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = GroqLLMAdapter()
    return _llm_client


def get_memory() -> MemoryPort:
    """Get memory instance."""
    global _memory
    if _memory is None:
        _memory = InMemoryMemoryAdapter()
    return _memory


def get_chat_service() -> ChatService:
    """Get chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(
            llm_client=get_llm_client(),
            memory=get_memory()
        )
    return _chat_service