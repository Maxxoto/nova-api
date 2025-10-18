"""FastAPI endpoints for Nova Agent API."""

import json
from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from ..llm_providers.groq_client import groq_client

# Create router
chat_router = APIRouter(prefix="/sse", tags=["chat"])


# Pydantic models for chat
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    thread_id: str = None


@chat_router.post("/chat-completion")
async def chat_completion_stream(request: ChatCompletionRequest, request_obj: Request):
    """Stream chat completion using Groq with LangGraph via Server-Sent Events."""

    async def event_generator():
        """Generate SSE events from Groq streaming response."""
        try:
            # Convert messages to dict format
            messages_dict = [
                {"role": msg.role, "content": msg.content} for msg in request.messages
            ]

            # Stream the response
            async for chunk in groq_client.stream_chat_completion(
                messages=messages_dict, thread_id=request.thread_id
            ):
                if await request_obj.is_disconnected():
                    break

                # Send each chunk as an SSE event
                yield {
                    "event": "message",
                    "data": json.dumps({"content": chunk, "type": "chunk"}),
                }

            # Send completion event
            yield {
                "event": "complete",
                "data": json.dumps({"type": "complete", "message": "Stream completed"}),
            }

        except Exception as e:
            # Send error event
            yield {
                "event": "error",
                "data": json.dumps(
                    {"type": "error", "message": f"Error during streaming: {str(e)}"}
                ),
            }

    return EventSourceResponse(event_generator())
