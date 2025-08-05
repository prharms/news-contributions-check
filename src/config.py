"""Configuration settings for news contribution check application."""

# Claude AI Model Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# API Configuration
CLAUDE_MAX_TOKENS = 2000
CLAUDE_TEMPERATURE = 0.1

# File Processing Configuration
DEFAULT_DATA_DIRECTORY = "data"
DEFAULT_OUTPUT_DIRECTORY = "output"
DEFAULT_CSV_FILENAME = "company_mentions.csv"
DEFAULT_SUMMARY_FILENAME = "summary_stats.csv"

# Text Processing Configuration
MAX_DESCRIPTION_LENGTH = 300
DEFAULT_DATE = "1900-01-01"
DEFAULT_SOURCE = "Unknown Source"