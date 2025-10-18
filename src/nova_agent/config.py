"""Configuration settings for Nova Agent API."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    api_title: str = "Nova Agent API"
    api_version: str = "0.1.0"
    api_description: str = "A powerful agent-based API service"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database Settings
    database_url: str = "postgresql://nova_user:nova_password@localhost:5432/nova_api"
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()