"""Use case for handling user prompts and orchestrating agent responses."""

from typing import AsyncGenerator, Dict, Any, Optional
from uuid import UUID

from ...core.entities.agent_state import AgentState
from ...core.entities.plan import Plan
from ...core.ports.planner_port import PlannerPort
from ...core.ports.executor_port import ExecutorPort
from ...core.ports.memory_port import MemoryPort
from ...core.policies.safety_policy import SafetyPolicy


class HandleUserPromptUseCase:
    """Use case for handling user prompts and orchestrating agent responses."""
    
    def __init__(
        self,
        planner: PlannerPort,
        executor: ExecutorPort,
        memory: MemoryPort,
        safety_policy: SafetyPolicy
    ):
        self.planner = planner
        self.executor = executor
        self.memory = memory
        self.safety_policy = safety_policy
    
    async def execute(
        self,
        prompt: str,
        agent_id: UUID,
        thread_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the use case to handle a user prompt."""
        
        # Get agent state
        agent_state = await self.memory.get_agent_state(agent_id)
        if not agent_state:
            yield {"error": "Agent not found"}
            return
        
        # Validate prompt safety
        if not self.safety_policy.validate_content(prompt):
            yield {"error": "Prompt contains unsafe content"}
            return
        
        # Store conversation in memory
        await self._store_conversation(thread_id, prompt, agent_state)
        
        # Create execution plan based on prompt
        plan = await self.planner.create_plan(prompt, agent_state)
        
        # Validate plan safety
        if not self.safety_policy.validate_plan(plan, agent_state):
            yield {"error": "Generated plan contains unsafe actions"}
            return
        
        # Execute the plan and stream results
        async for result in self.executor.execute_plan(plan, agent_state):
            yield result
        
        # Update agent state with new capabilities if any
        await self._update_agent_state(agent_state, plan)
    
    async def _store_conversation(
        self,
        thread_id: Optional[str],
        prompt: str,
        agent_state: AgentState
    ) -> None:
        """Store conversation in memory."""
        
        if thread_id:
            messages = [
                {"role": "user", "content": prompt},
                {"role": "system", "content": f"Agent: {agent_state.name}"}
            ]
            await self.memory.store_conversation(thread_id, messages)
    
    async def _update_agent_state(self, agent_state: AgentState, plan: Plan) -> None:
        """Update agent state based on executed plan."""
        
        # Extract new capabilities from plan execution
        new_capabilities = self._extract_capabilities_from_plan(plan)
        
        for capability in new_capabilities:
            if capability not in agent_state.capabilities:
                agent_state.add_capability(capability)
        
        # Update agent state in memory
        await self.memory.update_agent_state(
            agent_state.id,
            {"capabilities": agent_state.capabilities}
        )
    
    def _extract_capabilities_from_plan(self, plan: Plan) -> list[str]:
        """Extract new capabilities from executed plan."""
        
        capabilities = []
        for step in plan.steps:
            if step.status == "completed" and step.result:
                # Extract capability from step action and result
                capability = f"{step.action}_completed"
                capabilities.append(capability)
        
        return capabilities