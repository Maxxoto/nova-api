"""Groq LLM Adapter for hexagonal architecture."""

import logging
from typing import AsyncGenerator, Dict, Any, List, Optional

from langchain_groq import ChatGroq

from core.ports.llm_client_port import LLMClientPort
from infrastructure.config import settings


logger = logging.getLogger(__name__)


class GroqLLMAdapter(LLMClientPort):
    """Groq LLM adapter implementing LLMClientPort."""

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=0.7,
            streaming=True,
        )

    def invoke(self, messages: List[Any]) -> Any:
        """Invoke the LLM with messages and return response.
        
        Args:
            messages: List of messages to send to LLM
            
        Returns:
            LLM response object
        """
        return self.llm.invoke(messages)

    async def stream_chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion using Groq.
        
        Args:
            messages: List of chat messages
            thread_id: Optional thread ID for conversation context
            
        Yields:
            Dictionary containing content and thread_id
        """
        # Convert messages to LangChain format
        from langchain_core.messages import HumanMessage, SystemMessage
        
        langchain_messages = []
        for message in messages:
            if message["role"] == "user":
                langchain_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "system":
                langchain_messages.append(SystemMessage(content=message["content"]))
        
        # Stream the response
        async for chunk in self.llm.astream(langchain_messages):
            if hasattr(chunk, 'content'):
                yield {"content": chunk.content, "thread_id": thread_id or "default"}

    async def chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion using Groq.
        
        Args:
            messages: List of chat messages
            thread_id: Optional thread ID for conversation context
            
        Returns:
            Dictionary containing response and thread_id
        """
        # Convert messages to LangChain format
        from langchain_core.messages import HumanMessage, SystemMessage
        
        langchain_messages = []
        for message in messages:
            if message["role"] == "user":
                langchain_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "system":
                langchain_messages.append(SystemMessage(content=message["content"]))
        
        # Get the response
        response = self.llm.invoke(langchain_messages)
        
        return {
            "response": response.content,
            "thread_id": thread_id or "default",
            "memory_used": False,  # Memory is handled by orchestrator
        }
