"""Agent State Entity for hexagonal architecture."""

from typing import Annotated, Dict, Any
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage


class AgentState(Dict[str, Any]):
    """State for the chat graph."""
    
    messages: Annotated[list[AnyMessage], add_messages]