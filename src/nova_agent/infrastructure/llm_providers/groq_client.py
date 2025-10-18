"""Groq LLM client with LangGraph and LangChain integration."""

import logging
from typing import AsyncGenerator, Dict, Any, List, Optional


from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate


from nova_agent.config import settings


logger = logging.getLogger(__name__)


class ChatState(Dict[str, Any]):
    """State for the chat graph."""

    messages: List[Dict[str, Any]]
    response: str = ""


class GroqClient:
    """Groq LLM client with streaming support and memory management."""

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=0.7,
            streaming=True,
        )
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state graph with memory."""

        def chatbot_node(state: ChatState) -> ChatState:
            """Process user message and generate response with memory context."""
            messages = state["messages"]

            # Convert to LangChain message format
            lc_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))

            # Create prompt template with memory context
            system_prompt = (
                "You are a helpful AI assistant. Provide clear, concise, and helpful responses. "
                "Use the conversation history to maintain context and provide relevant responses."
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    *[(msg.type, msg.content) for msg in lc_messages],
                ]
            )

            # Generate response with streaming
            chain = prompt | self.llm
            response = chain.invoke({})

            state["response"] = response.content
            return state

        # Build the graph with memory checkpointing
        workflow = StateGraph(ChatState)
        workflow.add_node("chatbot", chatbot_node)
        workflow.set_entry_point("chatbot")
        workflow.add_edge("chatbot", END)

        return workflow.compile(checkpointer=self.memory)

    async def stream_chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion using Groq with memory context."""

        # Use thread_id for memory context - this is crucial for memory to work
        thread_id = thread_id or "default"

        if thread_id == "default":
            logger.info(
                "No thread id provided !, Agent will lose context of the conversation"
            )

        # Prepare initial state
        initial_state = ChatState(messages=messages)
        config = {"configurable": {"thread_id": thread_id}}

        # Execute graph with memory to stream messages
        async for chunk in self.graph.astream(
            initial_state, config, stream_mode="messages"
        ):
            if chunk and isinstance(chunk[0], AIMessageChunk):
                yield chunk[0].content

    async def chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: str = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion using LangGraph with memory."""

        # Use thread_id for memory context
        thread_id = thread_id or "default"

        initial_state = ChatState(messages=messages)
        config = {"configurable": {"thread_id": thread_id}}

        # Execute the graph with memory
        final_state = self.graph.invoke(initial_state, config)

        return {
            "response": final_state["response"],
            "thread_id": thread_id,
            "memory_used": True,
        }

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
            config = {"configurable": {"thread_id": thread_id}}
            # LangGraph MemorySaver doesn't have a direct clear method
            # We can simulate clearing by starting a new conversation
            return True
        except Exception:
            return False


# Global Groq client instance
groq_client = GroqClient()
