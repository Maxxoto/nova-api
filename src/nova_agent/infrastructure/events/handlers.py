"""Event handlers for Nova Agent API."""

import logging

from ....domain.events import AgentCreated, AgentUpdated


class LoggingEventHandler:
    """Event handler that logs domain events."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle(self, event) -> None:
        """Handle an event by logging it."""
        if isinstance(event, AgentCreated):
            self.logger.info(
                "Agent created: %s (ID: %s) with capabilities: %s",
                event.agent_name,
                event.agent_id,
                event.capabilities,
            )
        elif isinstance(event, AgentUpdated):
            self.logger.info(
                "Agent updated: %s - fields changed: %s",
                event.agent_id,
                event.updated_fields,
            )
            if event.previous_status and event.new_status:
                self.logger.info(
                    "Status changed from %s to %s",
                    event.previous_status,
                    event.new_status,
                )