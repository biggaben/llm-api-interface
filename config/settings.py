# config/settings.py
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any
import os
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # Base
    project_name: str = "llm-api-interface"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # API Keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    
    # Paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent,
        alias="BASE_DIR"
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / ".cache",
        alias="CACHE_DIR"
    )
    
    # API Configuration
    api_timeout: int = Field(default=30, alias="API_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT")
    
    # Cache Configuration
    CACHE_ENABLED: bool = Field(default=True)
    CACHE_TTL: int = Field(default=3600)
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        alias="LOG_FORMAT"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix=""
    )

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        settings = cls()
        settings.cache_dir.mkdir(parents=True, exist_ok=True)
        return settings

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key."""
        return getattr(self, key, default)

    @computed_field
    def cache_enabled(self) -> bool:
        """Alias for CACHE_ENABLED."""
        return self.CACHE_ENABLED

    @computed_field
    def cache_ttl(self) -> int:
        """Alias for CACHE_TTL."""
        return self.CACHE_TTL

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings.from_env()

# Create a singleton instance
settings = get_settings()