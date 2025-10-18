"""Nova Agent API - A powerful agent-based API service."""

__version__ = "0.1.0"
__author__ = "Nova Team"
__email__ = "nova@example.com"

from .config import settings
from .main import app

__all__ = ["app", "settings"]