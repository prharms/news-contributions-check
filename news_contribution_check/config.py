"""Configuration settings for news contribution check application."""

from datetime import datetime

# Claude AI Model Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# API Configuration
CLAUDE_MAX_TOKENS = 2000
CLAUDE_TEMPERATURE = 0.1

# File Processing Configuration
DEFAULT_DATA_DIRECTORY = "data"
DEFAULT_OUTPUT_DIRECTORY = "output"

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

DEFAULT_CSV_FILENAME = "company_mentions.csv"
DEFAULT_SUMMARY_FILENAME = "summary_stats.csv"

# Text Processing Configuration
MAX_DESCRIPTION_LENGTH = 300
DEFAULT_DATE = "1900-01-01"
DEFAULT_SOURCE = "Unknown Source"