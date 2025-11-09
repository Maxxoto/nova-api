"""Memory-specific dependency injection to break circular imports."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain.embeddings import init_embeddings

# Create singleton instances
_long_term_memory_store = None
_thread_memory_store = None


def get_longterm_memory_store():
    """Get shared in-memory store instance."""
    global _long_term_memory_store
    if _long_term_memory_store is None:
        embeddings = init_embeddings("ollama:nomic-embed-text")
        _long_term_memory_store = InMemoryStore(
            index={"embed": embeddings, "dims": "768"},
        )
    return _long_term_memory_store


def get_thread_memory():
    """Get shared in-memory store instance."""
    global _thread_memory_store
    if _thread_memory_store is None:
        _thread_memory_store = InMemorySaver()
    return _thread_memory_store
