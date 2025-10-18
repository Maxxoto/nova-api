"""FastAPI endpoints for Nova Agent API."""

import json
from uuid import UUID
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from ....application.dto import CreateAgentDTO, UpdateAgentDTO
from ....application.use_cases import CreateAgentUseCase, GetAgentUseCase, UpdateAgentUseCase
from ....application.services import EventPublisher
from ....domain.entities import Agent
from ....domain.events import AgentCreated, AgentUpdated
from ....domain.exceptions import AgentNotFound, InvalidAgentStatus
from ...database.repositories import SQLAgentRepository
from ...llm.groq_client import groq_client

# Create routers
agent_router = APIRouter(prefix="/agents", tags=["agents"])
chat_router = APIRouter(prefix="/sse", tags=["chat"])


# Pydantic models for chat
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    thread_id: str = None


def get_agent_repository():
    """Dependency for agent repository."""
    # In a real implementation, this would get a database session
    # For now, we'll return a mock repository
    return SQLAgentRepository(None)


def get_event_publisher():
    """Dependency for event publisher."""
    publisher = EventPublisher()
    # In a real implementation, we would subscribe actual event handlers
    return publisher


def get_create_agent_use_case(
    repo: SQLAgentRepository = Depends(get_agent_repository),
    publisher: EventPublisher = Depends(get_event_publisher),
):
    """Dependency for create agent use case."""
    return CreateAgentUseCase(repo, publisher)


def get_get_agent_use_case(repo: SQLAgentRepository = Depends(get_agent_repository)):
    """Dependency for get agent use case."""
    return GetAgentUseCase(repo)


def get_update_agent_use_case(
    repo: SQLAgentRepository = Depends(get_agent_repository),
    publisher: EventPublisher = Depends(get_event_publisher),
):
    """Dependency for update agent use case."""
    return UpdateAgentUseCase(repo, publisher)


@agent_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agent(
    dto: CreateAgentDTO,
    use_case: CreateAgentUseCase = Depends(get_create_agent_use_case),
):
    """Create a new agent."""
    try:
        agent = use_case.execute(dto)
        return {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat(),
        }
    except InvalidAgentStatus as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@agent_router.get("/{agent_id}")
async def get_agent(
    agent_id: UUID,
    use_case: GetAgentUseCase = Depends(get_get_agent_use_case),
):
    """Get an agent by ID."""
    try:
        agent = use_case.execute(agent_id)
        return {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat(),
        }
    except AgentNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@agent_router.put("/{agent_id}")
async def update_agent(
    agent_id: UUID,
    dto: UpdateAgentDTO,
    use_case: UpdateAgentUseCase = Depends(get_update_agent_use_case),
):
    """Update an agent."""
    try:
        agent = use_case.execute(agent_id, dto)
        return {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat(),
        }
    except AgentNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidAgentStatus as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@agent_router.get("/")
async def list_agents(repo: SQLAgentRepository = Depends(get_agent_repository)):
    """List all agents."""
    agents = repo.get_all()
    return [
        {
            "id": str(agent.id),
            "name": agent.name,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "status": agent.status,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat(),
        }
        for agent in agents
    ]


@chat_router.post("/chat-completion")
async def chat_completion_stream(
    request: ChatCompletionRequest,
    request_obj: Request
):
    """Stream chat completion using Groq with LangGraph via Server-Sent Events."""
    
    async def event_generator():
        """Generate SSE events from Groq streaming response."""
        try:
            # Convert messages to dict format
            messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            # Stream the response
            async for chunk in groq_client.stream_chat_completion(
                messages=messages_dict,
                thread_id=request.thread_id
            ):
                if await request_obj.is_disconnected():
                    break
                
                # Send each chunk as an SSE event
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "content": chunk,
                        "type": "chunk"
                    })
                }
            
            # Send completion event
            yield {
                "event": "complete",
                "data": json.dumps({
                    "type": "complete",
                    "message": "Stream completed"
                })
            }
            
        except Exception as e:
            # Send error event
            yield {
                "event": "error",
                "data": json.dumps({
                    "type": "error",
                    "message": f"Error during streaming: {str(e)}"
                })
            }
    
    return EventSourceResponse(event_generator())