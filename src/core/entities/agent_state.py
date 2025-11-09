"""Agent State Entity for hexagonal architecture."""

from typing import Annotated, Dict, Any, Optional, List
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from ..entities.plan import Plan


class AgentState(Dict[str, Any]):
    """State for the chat graph with enhanced workflow support."""

    messages: Annotated[list[AnyMessage], add_messages]
    intent: Optional[str] = None
    recalled_memory: Optional[List[Dict[str, Any]]] = None
    plan: Optional[Plan] = None
    needs_memory_recall: bool = False
    needs_planning: bool = False
    user_id: str = None
    thread_id: str = None
