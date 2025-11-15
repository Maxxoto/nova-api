"""Memory Recall Node for AI agent workflow with LangMem integration."""

import logging
from domain.entities.agent_state import AgentState
from domain.ports.memory_port import MemoryPort

logger = logging.getLogger(__name__)


class MemoryRecallNode:
    """Node that retrieves relevant memory for the conversation using LangMem."""

    def __init__(self, memory_adapter: MemoryPort):
        self.memory_adapter = memory_adapter

    async def recall_memory(self, state: AgentState) -> AgentState:
        """Recall relevant conversation memory using LangMem for long-term memory."""

        user_id = state.get("user_id")
        thread_id = state.get("thread_id")
        try:
            # Get short-term conversation history from memory adapter
            conversation_history = await self.memory_adapter.get_conversation_history(
                thread_id
            )

            # Get long-term memory summary using LangMem
            long_term_summary = await self.memory_adapter.get_long_term_summary(
                user_id, max_tokens=300
            )

            # Combine short-term and long-term memory
            recalled_memory = []

            # Add short-term memory (recent conversation)
            # TODO: Explore more about trim message and so on https://docs.langchain.com/oss/python/langchain/short-term-memory#trim-messages
            if conversation_history:
                relevant_memory = conversation_history[-5:]  # Last 5 messages
                recalled_memory.extend(relevant_memory)
                logger.info(
                    f"Recalled {len(relevant_memory)} short-term memory entries"
                )

            # Add long-term memory summary
            if long_term_summary:
                recalled_memory.append(
                    {
                        "role": "system",
                        "content": f"Long-term context summary: {long_term_summary}",
                    }
                )
                logger.info("Recalled long-term memory summary")

            state["recalled_memory"] = recalled_memory

            if not recalled_memory:
                logger.info("No memory found for user")

            return state

        except Exception as e:
            logger.error(f"Error recalling memory: {str(e)}")
            state["recalled_memory"] = []
            return state

    async def execute_node(self, state: AgentState) -> AgentState:
        """Recall relevant memory from longterm"""
        user_id = state.get("user_id", "default_user")

        logger.info(f"Initiating memory recall for user: {user_id}")
        try:
            # Use the MemoryRecallNode to recall relevant memory
            state = await self.recall_memory(state)
            logger.info(
                f"Memory recall node executed for user {user_id}, recalled {len(state.get('recalled_memory', []))} memory entries"
            )
        except Exception as e:
            logger.error(f"Error in memory recall node: {str(e)}")
            state["recalled_memory"] = []

        return state
