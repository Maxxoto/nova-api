"""Groq LLM client with LangGraph and LangChain integration."""

from typing import AsyncGenerator, Dict, Any, List


from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate


from nova_agent.config import settings


class ChatState(Dict[str, Any]):
    """State for the chat graph."""

    messages: List[Dict[str, Any]]
    response: str = ""


class GroqClient:
    """Groq LLM client with streaming support."""

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=0.7,
            streaming=True,
        )
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""

        def chatbot_node(state: ChatState) -> ChatState:
            """Process user message and generate response."""
            messages = state["messages"]

            # Convert to LangChain message format
            lc_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    lc_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    lc_messages.append(AIMessage(content=msg["content"]))

            # Create prompt template
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a helpful AI assistant. Provide clear, concise, and helpful responses.",
                    ),
                    *[(msg.type, msg.content) for msg in lc_messages],
                ]
            )

            # Generate response
            chain = prompt | self.llm
            response = chain.invoke({})

            state["response"] = response.content
            return state

        # Build the graph
        workflow = StateGraph(ChatState)
        workflow.add_node("chatbot", chatbot_node)
        workflow.set_entry_point("chatbot")
        workflow.add_edge("chatbot", END)

        return workflow.compile(checkpointer=self.memory)

    async def stream_chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: str = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion using Groq with LangGraph."""

        # Prepare initial state
        initial_state = ChatState(messages=messages)

        # Configure for streaming
        config = {"configurable": {"thread_id": thread_id or "default"}}

        # Create a simple streaming version without full LangGraph for now
        # since LangGraph streaming is more complex
        last_user_message = None
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break

        if last_user_message:
            # Use direct Groq streaming for simplicity
            stream = self.llm.astream(last_user_message)
            async for chunk in stream:
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

    async def chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: str = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion using LangGraph."""

        initial_state = ChatState(messages=messages)
        config = {"configurable": {"thread_id": thread_id or "default"}}

        # Execute the graph
        final_state = self.graph.invoke(initial_state, config)

        return {
            "response": final_state["response"],
            "thread_id": config["configurable"]["thread_id"],
        }


# Global Groq client instance
groq_client = GroqClient()
