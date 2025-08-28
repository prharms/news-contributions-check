"""Tests for custom exception classes."""

import pytest

from news_contribution_check.exceptions import (
    NewsContributionCheckError,
    ConfigurationError,
    DocumentProcessingError,
    ClaudeAPIError,
    CSVExportError,
    ValidationError,
)


class TestNewsContributionCheckError:
    """Test cases for base exception class."""

    def test_inheritance(self) -> None:
        """Test that base exception inherits from Exception."""
        error = NewsContributionCheckError("Test error")
        assert isinstance(error, Exception)

    def test_message_preservation(self) -> None:
        """Test that error message is preserved."""
        message = "Test error message"
        error = NewsContributionCheckError(message)
        assert str(error) == message


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    def test_inheritance(self) -> None:
        """Test that ConfigurationError inherits from base exception."""
        error = ConfigurationError("Configuration error")
        assert isinstance(error, NewsContributionCheckError)

    def test_message_preservation(self) -> None:
        """Test that error message is preserved."""
        message = "Invalid configuration"
        error = ConfigurationError(message)
        assert str(error) == message


class TestDocumentProcessingError:
    """Test cases for DocumentProcessingError."""

    def test_inheritance(self) -> None:
        """Test that DocumentProcessingError inherits from base exception."""
        error = DocumentProcessingError("Document processing error")
        assert isinstance(error, NewsContributionCheckError)

    def test_initialization_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        message = "Failed to process document"
        file_path = "/path/to/document.docx"
        cause = ValueError("Invalid format")
        
        error = DocumentProcessingError(message, file_path, cause)
        
        assert str(error) == message
        assert error.file_path == file_path
        assert error.cause == cause

    def test_initialization_without_optional_parameters(self) -> None:
        """Test initialization without optional parameters."""
        message = "Failed to process document"
        
        error = DocumentProcessingError(message)
        
        assert str(error) == message
        assert error.file_path is None
        assert error.cause is None

    def test_initialization_with_file_path_only(self) -> None:
        """Test initialization with file_path only."""
        message = "Failed to process document"
        file_path = "/path/to/document.docx"
        
        error = DocumentProcessingError(message, file_path=file_path)
        
        assert str(error) == message
        assert error.file_path == file_path
        assert error.cause is None

    def test_initialization_with_cause_only(self) -> None:
        """Test initialization with cause only."""
        message = "Failed to process document"
        cause = ValueError("Invalid format")
        
        error = DocumentProcessingError(message, cause=cause)
        
        assert str(error) == message
        assert error.file_path is None
        assert error.cause == cause


class TestClaudeAPIError:
    """Test cases for ClaudeAPIError."""

    def test_inheritance(self) -> None:
        """Test that ClaudeAPIError inherits from base exception."""
        error = ClaudeAPIError("Claude API error")
        assert isinstance(error, NewsContributionCheckError)

    def test_initialization_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        message = "API call failed"
        api_response = '{"error": "rate limit exceeded"}'
        cause = ConnectionError("Network timeout")
        
        error = ClaudeAPIError(message, api_response, cause)
        
        assert str(error) == message
        assert error.api_response == api_response
        assert error.cause == cause

    def test_initialization_without_optional_parameters(self) -> None:
        """Test initialization without optional parameters."""
        message = "API call failed"
        
        error = ClaudeAPIError(message)
        
        assert str(error) == message
        assert error.api_response is None
        assert error.cause is None

    def test_initialization_with_api_response_only(self) -> None:
        """Test initialization with api_response only."""
        message = "API call failed"
        api_response = '{"error": "rate limit exceeded"}'
        
        error = ClaudeAPIError(message, api_response=api_response)
        
        assert str(error) == message
        assert error.api_response == api_response
        assert error.cause is None

    def test_initialization_with_cause_only(self) -> None:
        """Test initialization with cause only."""
        message = "API call failed"
        cause = ConnectionError("Network timeout")
        
        error = ClaudeAPIError(message, cause=cause)
        
        assert str(error) == message
        assert error.api_response is None
        assert error.cause == cause


class TestCSVExportError:
    """Test cases for CSVExportError."""

    def test_inheritance(self) -> None:
        """Test that CSVExportError inherits from base exception."""
        error = CSVExportError("CSV export error")
        assert isinstance(error, NewsContributionCheckError)

    def test_initialization_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        message = "Failed to export CSV"
        file_path = "/path/to/output.csv"
        cause = PermissionError("Permission denied")
        
        error = CSVExportError(message, file_path, cause)
        
        assert str(error) == message
        assert error.file_path == file_path
        assert error.cause == cause

    def test_initialization_without_optional_parameters(self) -> None:
        """Test initialization without optional parameters."""
        message = "Failed to export CSV"
        
        error = CSVExportError(message)
        
        assert str(error) == message
        assert error.file_path is None
        assert error.cause is None

    def test_initialization_with_file_path_only(self) -> None:
        """Test initialization with file_path only."""
        message = "Failed to export CSV"
        file_path = "/path/to/output.csv"
        
        error = CSVExportError(message, file_path=file_path)
        
        assert str(error) == message
        assert error.file_path == file_path
        assert error.cause is None

    def test_initialization_with_cause_only(self) -> None:
        """Test initialization with cause only."""
        message = "Failed to export CSV"
        cause = PermissionError("Permission denied")
        
        error = CSVExportError(message, cause=cause)
        
        assert str(error) == message
        assert error.file_path is None
        assert error.cause == cause


class TestValidationError:
    """Test cases for ValidationError."""

    def test_inheritance(self) -> None:
        """Test that ValidationError inherits from base exception."""
        error = ValidationError("Validation error")
        assert isinstance(error, NewsContributionCheckError)

    def test_initialization_with_all_parameters(self) -> None:
        """Test initialization with all parameters."""
        message = "Invalid input"
        field_name = "email"
        invalid_value = "not-an-email"
        
        error = ValidationError(message, field_name, invalid_value)
        
        assert str(error) == message
        assert error.field_name == field_name
        assert error.invalid_value == invalid_value

    def test_initialization_without_optional_parameters(self) -> None:
        """Test initialization without optional parameters."""
        message = "Invalid input"
        
        error = ValidationError(message)
        
        assert str(error) == message
        assert error.field_name is None
        assert error.invalid_value is None

    def test_initialization_with_field_name_only(self) -> None:
        """Test initialization with field_name only."""
        message = "Invalid input"
        field_name = "email"
        
        error = ValidationError(message, field_name=field_name)
        
        assert str(error) == message
        assert error.field_name == field_name
        assert error.invalid_value is None

    def test_initialization_with_invalid_value_only(self) -> None:
        """Test initialization with invalid_value only."""
        message = "Invalid input"
        invalid_value = "not-an-email"
        
        error = ValidationError(message, invalid_value=invalid_value)
        
        assert str(error) == message
        assert error.field_name is None
        assert error.invalid_value == invalid_value


class TestExceptionChaining:
    """Test cases for exception chaining behavior."""

    def test_exception_chaining_with_cause(self) -> None:
        """Test that exceptions can be chained with cause."""
        original_error = ValueError("Original error")
        
        try:
            raise original_error
        except ValueError as e:
            with pytest.raises(DocumentProcessingError) as exc_info:
                raise DocumentProcessingError("Processing failed", cause=e) from e
            
            error = exc_info.value
            assert error.cause == original_error
            assert error.__cause__ == original_error

    def test_exception_chaining_without_cause(self) -> None:
        """Test that exceptions can be chained without explicit cause."""
        original_error = ValueError("Original error")
        
        try:
            raise original_error
        except ValueError as e:
            with pytest.raises(DocumentProcessingError) as exc_info:
                raise DocumentProcessingError("Processing failed") from e
            
            error = exc_info.value
            assert error.cause is None
            assert error.__cause__ == original_error
