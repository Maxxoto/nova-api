"""Advanced LangGraph Orchestrator with workflow nodes."""

import logging
import uuid
import os
from typing import AsyncGenerator, Dict, Any, List, Optional

from application.services.nodes.intent_detector import IntentDetector
from application.services.nodes.llm_node import LLMNode
from application.services.nodes.memory_recall_node import MemoryRecallNode
from application.services.nodes.memory_write_node import MemoryWriteNode
from langchain_core.messages import AIMessageChunk, SystemMessage
from langgraph.func import START
from langgraph.graph import StateGraph, END
from opik.integrations.langchain import OpikTracer

from domain.entities.agent_state import AgentState
from domain.ports.llm_client_port import LLMClientPort
from domain.ports.memory_port import MemoryPort

from infrastructure.memory_di import get_thread_memory, get_longterm_memory_store
from domain.entities.plan import Plan  # Import Plan


logger = logging.getLogger(__name__)


class LangGraphOrchestrator:
    """Advanced LangGraph orchestrator with workflow nodes for AI agent."""

    def __init__(self, llm_client: LLMClientPort, memory_adapter: MemoryPort):
        self.llm_client = llm_client
        self.memory_adapter = memory_adapter
        self.memory = get_thread_memory()  # Call the function to get the instance
        self.lt_memory = get_longterm_memory_store()

        # Initialize observability
        self._setup_observability()

        # Initialize workflow nodes
        self.intent_detector = IntentDetector(llm_client, "qwen/qwen3-32b")
        self.memory_recall_node = MemoryRecallNode(memory_adapter)
        self.llm_node = LLMNode(llm_client)
        self.memory_write_node = MemoryWriteNode(memory_adapter)

        self.graph = self._build_graph()

    def _route_memory_recall(self, state: AgentState) -> str:
        """Route workflow based on memory recall needs."""
        if state.get("needs_memory_recall", False):
            logger.info("Routing to memory recall node (internal)")
            return "memory_recall_node"
        else:
            logger.info("Routing to planner node (no memory recall needed) (internal)")
            return "planner_node"

    def _create_plan_and_prompt(self, state: AgentState) -> AgentState:
        """Create execution plan and build enhanced prompt internally."""
        latest_message = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, "type") and msg.type == "human":
                latest_message = msg.content
                break

        if not latest_message:
            return state

        plan = Plan(
            name=f"Plan for: {latest_message[:50]}...",
            description="Generated plan based on user request",
        )

        if state.get("needs_planning", False):
            plan.add_step(
                description="Analyze the user's request and requirements",
                action="analyze_request",
            )
            plan.add_step(
                description="Generate step-by-step approach", action="generate_approach"
            )
            plan.add_step(
                description="Execute the plan and provide results",
                action="execute_plan",
            )

        state["plan"] = plan

        enhanced_prompt = self._build_enhanced_prompt(state, latest_message)

        state["messages"].insert(0, SystemMessage(content=enhanced_prompt))

        logger.info(f"Created internal plan with {len(plan.steps)} steps")
        return state

    def _build_enhanced_prompt(self, state: AgentState, user_message: str) -> str:
        """Build enhanced prompt with memory and plan context internally."""
        prompt_parts = [
            "You are a helpful AI assistant. Provide clear, concise, and helpful responses.",
            "Use the conversation history and context below to maintain context and provide relevant responses.",
        ]

        if state.get("recalled_memory"):
            prompt_parts.append("\nPrevious conversation context:")
            for memory in state["recalled_memory"]:
                role = memory.get("role", "unknown")
                content = memory.get("content", "")
                prompt_parts.append(f"{role}: {content}")

        if state.get("plan"):
            plan = state["plan"]
            prompt_parts.append(f"\nCurrent plan: {plan.name}")
            if plan.description:
                prompt_parts.append(f"Plan description: {plan.description}")

        prompt_parts.append(f"\nCurrent user message: {user_message}")

        return "\n".join(prompt_parts)

    def _build_graph(self):
        """Build the advanced LangGraph state graph with workflow nodes."""

        # Build the graph with workflow nodes
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("intent_detector", self.intent_detector.detect_intent)
        workflow.add_node("memory_recall_node", self.memory_recall_node.execute_node)
        workflow.add_node("planner_node", self._create_plan_and_prompt)
        workflow.add_node("llm_node", self.llm_node.execute_node)
        workflow.add_node("memory_write_node", self.memory_write_node.execute_node)

        # Define workflow edges
        workflow.add_edge(START, "intent_detector")
        workflow.add_conditional_edges(
            "intent_detector",
            self._route_memory_recall,  # Use internal routing method
            {
                "memory_recall_node": "memory_recall_node",
                "planner_node": "planner_node",  # Route to planner node
            },
        )

        workflow.add_edge(
            "memory_recall_node", "llm_node"
        )  # If memory recalled, then go to LLM
        workflow.add_edge("planner_node", "llm_node")  # After planning, go to LLM
        # TODO: ADD conditional edge to plan either to write memory or not
        workflow.add_edge("llm_node", "memory_write_node")
        workflow.add_edge("memory_write_node", END)

        compiled_graph = workflow.compile(
            checkpointer=self.memory, store=self.lt_memory
        )

        return compiled_graph

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat completion using advanced workflow."""

        thread_id = thread_id or "default"
        if thread_id == "default":
            thread_id = str(uuid.uuid4())

        if not user_id:
            user_id = "default_user"
        # Prepare initial state
        initial_state = AgentState(
            messages=messages, thread_id=thread_id, user_id=user_id
        )
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}

        # Add OpikTracer to config if available
        if hasattr(self, "opik_tracer") and self.opik_tracer:
            config["callbacks"] = [self.opik_tracer]

        # Collect complete response
        complete_response = ""

        # Execute graph with memory to stream messages
        async for chunk in self.graph.astream(
            initial_state, config, stream_mode="messages"
        ):
            if chunk and isinstance(chunk[0], AIMessageChunk):
                chunk_content = chunk[0].content
                complete_response += chunk_content
                yield {"content": chunk_content, "thread_id": thread_id}

        logger.info(f"Completed advanced workflow for thread {thread_id}")

        # Log workflow metrics for streaming completion
        self._log_workflow_metrics(initial_state, thread_id, complete_response)

    async def chat_completion(
        self, messages: List[Dict[str, Any]], thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Non-streaming chat completion using advanced workflow."""

        thread_id = thread_id or "default"

        initial_state = AgentState(messages=messages, thread_id=thread_id)
        config = {"configurable": {"thread_id": thread_id}}

        # Add OpikTracer to config if available
        if hasattr(self, "opik_tracer") and self.opik_tracer:
            config["callbacks"] = [self.opik_tracer]

        # Execute the graph with memory
        final_state = self.graph.invoke(initial_state, config)

        # Extract response from messages
        response_content = ""
        if "messages" in final_state and final_state["messages"]:
            # Get the last AI message content
            for msg in reversed(final_state["messages"]):
                if hasattr(msg, "content") and msg.content:
                    response_content = msg.content
                    break

        # Log workflow metrics for non-streaming completion
        self._log_workflow_metrics(final_state, thread_id, response_content)

        return {
            "response": response_content,
            "thread_id": thread_id,
            "memory_used": True,
            "workflow_completed": True,
        }

    def _setup_observability(self):
        """Setup Opik observability."""
        try:
            # Setup Opik Tracer
            opik_api_key = os.getenv("OPIK_API_KEY")
            if opik_api_key:
                # Configure Opik first - only API key is needed
                import opik

                opik.configure(api_key=opik_api_key, workspace="ahmat-dani-setiawan")

                # Then create the tracer
                self.opik_tracer = OpikTracer()
                logger.info("Opik tracer initialized successfully")
            else:
                logger.warning("OPIK_API_KEY not found, Opik observability disabled")
                self.opik_tracer = None

        except Exception as e:
            logger.error(f"Failed to initialize observability: {str(e)}")
            self.opik_tracer = None

    def _log_workflow_metrics(
        self, state: AgentState, thread_id: str, response_content: str
    ):
        """Log workflow metrics."""
        # Opik automatically logs metrics through the tracer
        logger.info(
            f"Workflow completed for thread {thread_id}, response length: {len(response_content)}"
        )
