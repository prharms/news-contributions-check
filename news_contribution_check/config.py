"""Configuration settings for news contribution check application."""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .exceptions import ConfigurationError


@dataclass
class APIConfig:
    """API configuration settings."""
    
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2000
    temperature: float = 0.1
    
    def validate(self) -> None:
        """Validate API configuration."""
        if self.max_tokens <= 0:
            raise ConfigurationError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 1.0:
            raise ConfigurationError("temperature must be between 0.0 and 1.0")


@dataclass
class ProcessingConfig:
    """File processing configuration settings."""
    
    data_directory: str = "data"
    output_directory: str = "output"
    max_description_length: int = 300
    default_date: str = "1900-01-01"
    default_source: str = "Unknown Source"
    
    def validate(self) -> None:
        """Validate processing configuration."""
        if self.max_description_length <= 0:
            raise ConfigurationError("max_description_length must be positive")
        if not self.default_date or not self._is_valid_date_format(self.default_date):
            raise ConfigurationError("default_date must be in YYYY-MM-DD format")
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is in valid YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class AppConfig:
    """Main application configuration that combines all settings."""
    
    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self.api = APIConfig()
        self.processing = ProcessingConfig()
        self._validate()
    
    def _validate(self) -> None:
        """Validate all configuration sections."""
        self.api.validate()
        self.processing.validate()
    
    def get_api_key(self) -> str:
        """Get API key from environment variables.
        
        Returns:
            API key string
            
        Raises:
            ConfigurationError: If API key is not found
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Set it in your .env file or environment."
            )
        return api_key
    
    @property
    def data_directory(self) -> str:
        """Get data directory path."""
        return self.processing.data_directory
    
    @property
    def output_directory(self) -> str:
        """Get output directory path."""
        return self.processing.output_directory
    
    @property
    def max_description_length(self) -> int:
        """Get maximum description length."""
        return self.processing.max_description_length
    
    @property
    def default_date(self) -> str:
        """Get default date value."""
        return self.processing.default_date
    
    @property
    def default_source(self) -> str:
        """Get default source value."""
        return self.processing.default_source


def get_timestamped_filename(base_name: str, extension: str = "csv") -> str:
    """Generate a timestamped filename.
    
    Args:
        base_name: Base name for the file (e.g., "company_mentions")
        extension: File extension (default: "csv")
        
    Returns:
        Timestamped filename (e.g., "company_mentions_20250115_143052.csv")
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


