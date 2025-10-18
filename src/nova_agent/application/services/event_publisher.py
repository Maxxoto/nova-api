"""Event publisher service."""

from typing import Protocol

from ...domain.events import AgentCreated, AgentUpdated


class EventHandler(Protocol):
    """Protocol defining event handler interface."""
    
    def handle(self, event) -> None:
        """Handle an event."""
        ...


class EventPublisher:
    """Service for publishing domain events."""
    
    def __init__(self):
        self._handlers = {
            AgentCreated: [],
            AgentUpdated: [],
        }
    
    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].append(handler)
    
    def publish(self, event) -> None:
        """Publish an event to all subscribed handlers."""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler.handle(event)