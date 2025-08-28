"""Custom exceptions for the news contribution check application."""


class NewsContributionCheckError(Exception):
    """Base exception for all application errors."""
    pass


class ConfigurationError(NewsContributionCheckError):
    """Raised when configuration is invalid or missing."""
    pass


class DocumentProcessingError(NewsContributionCheckError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, file_path: str = None, cause: Exception = None):
        super().__init__(message)
        self.file_path = file_path
        self.cause = cause


class ClaudeAPIError(NewsContributionCheckError):
    """Raised when Claude API calls fail."""
    
    def __init__(self, message: str, api_response: str = None, cause: Exception = None):
        super().__init__(message)
        self.api_response = api_response
        self.cause = cause


class CSVExportError(NewsContributionCheckError):
    """Raised when CSV export operations fail."""
    
    def __init__(self, message: str, file_path: str = None, cause: Exception = None):
        super().__init__(message)
        self.file_path = file_path
        self.cause = cause


class ValidationError(NewsContributionCheckError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field_name: str = None, invalid_value: str = None):
        super().__init__(message)
        self.field_name = field_name
        self.invalid_value = invalid_value
