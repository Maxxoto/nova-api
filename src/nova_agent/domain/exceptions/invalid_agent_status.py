"""Invalid agent status exception."""


class InvalidAgentStatus(Exception):
    """Exception raised when an invalid agent status is provided."""
    
    def __init__(self, status: str):
        self.status = status
        super().__init__(
            f"Invalid agent status: {status}. Must be one of: active, inactive, maintenance"
        )