"""Dependency Injection for hexagonal architecture with singleton pattern."""

import logging
import os
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.store.base import BaseStore
from langchain.embeddings import init_embeddings


from domain.ports.llm_client_port import LLMClientPort
from domain.ports.memory_port import MemoryPort
from application.usecases.chat_service import ChatService
from infrastructure.adapters.llm_providers.groq import GroqLLMAdapter
from infrastructure.adapters.memory.in_memory_adapter import InMemoryMemoryAdapter
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


class DependencyContainer:
    """Singleton dependency container for managing all service instances."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._llm_client = None
            self._memory = None
            self._chat_service = None
            self._long_term_memory_store = None
            self._thread_memory_store = None
            self._initialized = True

    def get_llm_client(self) -> LLMClientPort:
        """Get LLM client instance."""
        if self._llm_client is None:
            self._llm_client = GroqLLMAdapter()

        return self._llm_client

    async def get_longterm_memory_store(self) -> BaseStore:
        """Get shared in-memory store instance."""
        if self._long_term_memory_store is None:
            embeddings = init_embeddings("ollama:nomic-embed-text")
            logger.debug(f"Embeddings initialized: {embeddings is not None}")

            # Create async connection pool for better performance
            self._conn_pool = AsyncConnectionPool(
                conninfo=os.getenv("POSTGRES_URL"),
                min_size=1,
                max_size=10,
                open=False,
            )
            # Open the pool explicitly (required for newer versions)
            await self._conn_pool.open()

            # Create PostgresStore instance with vector indexing for semantic search
            self._long_term_memory_store = AsyncPostgresStore(
                conn=self._conn_pool,
                index={
                    "dims": 768,
                    "embed": embeddings,
                    "fields": ["content"],
                    "distance_type": "cosine",
                },
            )

            await self._long_term_memory_store.setup()

        return self._long_term_memory_store

    def get_thread_memory(self):
        """Get shared in-memory store instance."""
        if self._thread_memory_store is None:
            self._thread_memory_store = InMemorySaver()
        return self._thread_memory_store

    async def get_memory(self) -> MemoryPort:
        """Get memory instance."""
        if self._memory is None:
            self._memory = InMemoryMemoryAdapter(
                llm_client=self.get_llm_client(),
                thread_memory_saver=self.get_thread_memory(),
                longterm_memory_store=await self.get_longterm_memory_store(),
            )
        return self._memory

    async def get_chat_service(self) -> ChatService:
        """Get chat service instance."""
        if self._chat_service is None:
            self._chat_service = ChatService(
                llm_client=self.get_llm_client(),
                memory=await self.get_memory(),
                thread_memory=self.get_thread_memory(),
                longterm_memory=await self.get_longterm_memory_store(),
            )

        return self._chat_service


# Global singleton instance
_container = DependencyContainer()


# Public API functions for backward compatibility
def get_llm_client() -> LLMClientPort:
    """Get LLM client instance."""
    return _container.get_llm_client()


async def get_memory() -> MemoryPort:
    """Get memory instance."""
    return await _container.get_memory()


async def get_chat_service() -> ChatService:
    """Get chat service instance."""
    return await _container.get_chat_service()


async def get_longterm_memory_store():
    """Get shared in-memory store instance."""
    return await _container.get_longterm_memory_store()


def get_thread_memory():
    """Get shared in-memory store instance."""
    return _container.get_thread_memory()
