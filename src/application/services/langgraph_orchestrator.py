"""LangGraph Orchestrator Service for hexagonal architecture."""

import logging
import uuid
from typing import AsyncGenerator, Dict, Any, List, Optional

from langchain_core.messages import (
    AIMessageChunk,
    SystemMessage,
)
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import START
from langgraph.graph import StateGraph, END

from core.entities.agent_state import AgentState
from core.ports.llm_client_port import LLMClientPort


logger = logging.getLogger(__name__)


class LangGraphOrchestrator:
    """LangGraph orchestrator for managing agent workflows and state."""

    def __init__(self, llm_client: LLMClientPort):
        self.llm_client = llm_client
        self.memory = InMemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state graph with memory."""

        def agent_node(state: dict):
            system_prompt = (
                "You are a helpful AI assistant. Provide clear, concise, and helpful responses. "
                "Use the conversation history to maintain context and provide relevant responses."
            )
            messages = state["messages"]
            # Ensure system_prompt is included in the conversation
            if messages and not isinstance(messages[0], SystemMessage):
                messages_to_send = [system_prompt] + messages
            else:
                messages_to_send = messages

            # Use the LLM client to get the response
            response = self.llm_client.invoke(messages_to_send)
            return {"messages": [response]}

        # Build the graph with memory checkpointing
        workflow = StateGraph(AgentState)

        workflow.add_node("chatbot", agent_node)

        workflow.add_edge(START, "chatbot")
        workflow.add_edge("chatbot", END)

        return workflow.compile(checkpointer=self.memory)

    async def stream_chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion using LangGraph with memory context."""

        # Use thread_id for memory context - this is crucial for memory to work
        thread_id = thread_id or "default"

        if thread_id == "default":
            # Generate uuid v4
            thread_id = str(uuid.uuid4())

        # Prepare initial state
        initial_state = AgentState(messages=messages)
        config = {"configurable": {"thread_id": thread_id}}

        # Collect complete response for message history update
        complete_response = ""

        # Execute graph with memory to stream messages
        async for chunk in self.graph.astream(
            initial_state, config, stream_mode="messages"
        ):
            if chunk and isinstance(chunk[0], AIMessageChunk):
                chunk_content = chunk[0].content
                complete_response += chunk_content
                yield {"content": chunk_content, "thread_id": thread_id}

        # Update message history after streaming completes
        await self._update_message_history(thread_id, messages, complete_response)

    async def chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion using LangGraph with memory."""

        # Use thread_id for memory context
        thread_id = thread_id or "default"

        initial_state = AgentState(messages=messages)
        config = {"configurable": {"thread_id": thread_id}}

        # Execute the graph with memory
        final_state = self.graph.invoke(initial_state, config)

        # Extract response from messages - final_state is a dict
        response_content = ""
        if "messages" in final_state and final_state["messages"]:
            # Get the last AI message content
            for msg in reversed(final_state["messages"]):
                if hasattr(msg, 'content') and msg.content:
                    response_content = msg.content
                    break

        return {
            "response": response_content,
            "thread_id": thread_id,
            "memory_used": True,
        }

    async def _update_message_history(
        self,
        thread_id: str,
        user_messages: List[Dict[str, Any]],
        assistant_response: str,
    ) -> None:
        """Update message history with user messages and assistant response."""
        try:
            # Get chat history for the thread
            from langchain_core.chat_history import InMemoryChatMessageHistory

            chat_history = InMemoryChatMessageHistory()

            # Add user messages to history
            for message in user_messages:
                if message["role"] == "user":
                    chat_history.add_user_message(message["content"])

            # Add assistant response to history
            if assistant_response:
                chat_history.add_ai_message(assistant_response)

            logger.info(f"Updated message history for thread {thread_id}")

        except Exception as e:
            logger.error(
                f"Failed to update message history for thread {thread_id}: {str(e)}"
            )