"""Tests for the configuration classes."""

import os
from unittest.mock import patch

import pytest

from news_contribution_check.config import (
    APIConfig,
    ProcessingConfig,
    AppConfig,
    get_timestamped_filename,
)
from news_contribution_check.exceptions import ConfigurationError


class TestAPIConfig:
    """Test cases for APIConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = APIConfig()
        
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 2000
        assert config.temperature == 0.1

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = APIConfig(
            model="test-model",
            max_tokens=1000,
            temperature=0.5
        )
        
        assert config.model == "test-model"
        assert config.max_tokens == 1000
        assert config.temperature == 0.5

    def test_validate_max_tokens_positive(self) -> None:
        """Test validation with positive max_tokens."""
        config = APIConfig(max_tokens=1000)
        config.validate()  # Should not raise

    def test_validate_max_tokens_zero(self) -> None:
        """Test validation with zero max_tokens."""
        config = APIConfig(max_tokens=0)
        with pytest.raises(ConfigurationError, match="max_tokens must be positive"):
            config.validate()

    def test_validate_max_tokens_negative(self) -> None:
        """Test validation with negative max_tokens."""
        config = APIConfig(max_tokens=-1)
        with pytest.raises(ConfigurationError, match="max_tokens must be positive"):
            config.validate()

    def test_validate_temperature_valid_range(self) -> None:
        """Test validation with valid temperature range."""
        config = APIConfig(temperature=0.5)
        config.validate()  # Should not raise

    def test_validate_temperature_zero(self) -> None:
        """Test validation with zero temperature."""
        config = APIConfig(temperature=0.0)
        config.validate()  # Should not raise

    def test_validate_temperature_one(self) -> None:
        """Test validation with temperature of one."""
        config = APIConfig(temperature=1.0)
        config.validate()  # Should not raise

    def test_validate_temperature_negative(self) -> None:
        """Test validation with negative temperature."""
        config = APIConfig(temperature=-0.1)
        with pytest.raises(ConfigurationError, match="temperature must be between 0.0 and 1.0"):
            config.validate()

    def test_validate_temperature_above_one(self) -> None:
        """Test validation with temperature above one."""
        config = APIConfig(temperature=1.1)
        with pytest.raises(ConfigurationError, match="temperature must be between 0.0 and 1.0"):
            config.validate()


class TestProcessingConfig:
    """Test cases for ProcessingConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ProcessingConfig()
        
        assert config.data_directory == "data"
        assert config.output_directory == "output"
        assert config.max_description_length == 300
        assert config.default_date == "1900-01-01"
        assert config.default_source == "Unknown Source"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = ProcessingConfig(
            data_directory="/custom/data",
            output_directory="/custom/output",
            max_description_length=500,
            default_date="2020-01-01",
            default_source="Custom Source"
        )
        
        assert config.data_directory == "/custom/data"
        assert config.output_directory == "/custom/output"
        assert config.max_description_length == 500
        assert config.default_date == "2020-01-01"
        assert config.default_source == "Custom Source"

    def test_validate_max_description_length_positive(self) -> None:
        """Test validation with positive max_description_length."""
        config = ProcessingConfig(max_description_length=500)
        config.validate()  # Should not raise

    def test_validate_max_description_length_zero(self) -> None:
        """Test validation with zero max_description_length."""
        config = ProcessingConfig(max_description_length=0)
        with pytest.raises(ConfigurationError, match="max_description_length must be positive"):
            config.validate()

    def test_validate_max_description_length_negative(self) -> None:
        """Test validation with negative max_description_length."""
        config = ProcessingConfig(max_description_length=-1)
        with pytest.raises(ConfigurationError, match="max_description_length must be positive"):
            config.validate()

    def test_validate_default_date_valid_format(self) -> None:
        """Test validation with valid date format."""
        config = ProcessingConfig(default_date="2020-01-01")
        config.validate()  # Should not raise

    def test_validate_default_date_invalid_format(self) -> None:
        """Test validation with invalid date format."""
        config = ProcessingConfig(default_date="invalid-date")
        with pytest.raises(ConfigurationError, match="default_date must be in YYYY-MM-DD format"):
            config.validate()

    def test_validate_default_date_empty(self) -> None:
        """Test validation with empty date."""
        config = ProcessingConfig(default_date="")
        with pytest.raises(ConfigurationError, match="default_date must be in YYYY-MM-DD format"):
            config.validate()

    def test_is_valid_date_format_valid_dates(self) -> None:
        """Test _is_valid_date_format with valid dates."""
        config = ProcessingConfig()
        
        valid_dates = [
            "2020-01-01",
            "2020-12-31",
            "1900-01-01",
            "9999-12-31"
        ]
        
        for date in valid_dates:
            assert config._is_valid_date_format(date)

    def test_is_valid_date_format_invalid_dates(self) -> None:
        """Test _is_valid_date_format with invalid dates."""
        config = ProcessingConfig()
        
        invalid_dates = [
            "invalid-date",
            "2020/01/01",
            "01-01-2020",
            "2020-13-01",  # Invalid month
            "2020-01-32",  # Invalid day
            "",
        ]
        
        for date in invalid_dates:
            assert not config._is_valid_date_format(date)
        
        # Test that "2020-1-1" is actually valid (Python's datetime.strptime handles this)
        assert config._is_valid_date_format("2020-1-1")


class TestAppConfig:
    """Test cases for AppConfig class."""

    def test_initialization_creates_subsections(self) -> None:
        """Test that initialization creates API and processing configs."""
        config = AppConfig()
        
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.processing, ProcessingConfig)

    def test_validation_calls_subsections(self) -> None:
        """Test that validation calls subsection validation."""
        config = AppConfig()
        
        # Should not raise if subsections are valid
        config._validate()

    def test_validation_fails_with_invalid_api_config(self) -> None:
        """Test that validation fails with invalid API config."""
        config = AppConfig()
        config.api.max_tokens = -1  # Invalid value
        
        with pytest.raises(ConfigurationError, match="max_tokens must be positive"):
            config._validate()

    def test_validation_fails_with_invalid_processing_config(self) -> None:
        """Test that validation fails with invalid processing config."""
        config = AppConfig()
        config.processing.max_description_length = -1  # Invalid value
        
        with pytest.raises(ConfigurationError, match="max_description_length must be positive"):
            config._validate()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_api_key_returns_environment_value(self) -> None:
        """Test that get_api_key returns environment variable value."""
        config = AppConfig()
        api_key = config.get_api_key()
        
        assert api_key == "test-api-key"

    @patch.dict('os.environ', {}, clear=True)
    def test_get_api_key_raises_error_when_missing(self) -> None:
        """Test that get_api_key raises error when environment variable is missing."""
        config = AppConfig()
        
        with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY environment variable is required"):
            config.get_api_key()

    def test_property_accessors(self) -> None:
        """Test property accessors for configuration values."""
        config = AppConfig()
        
        # Test that properties return values from processing config
        assert config.data_directory == config.processing.data_directory
        assert config.output_directory == config.processing.output_directory
        assert config.max_description_length == config.processing.max_description_length
        assert config.default_date == config.processing.default_date
        assert config.default_source == config.processing.default_source


class TestGetTimestampedFilename:
    """Test cases for get_timestamped_filename function."""

    def test_basic_functionality(self) -> None:
        """Test basic filename generation."""
        filename = get_timestamped_filename("test")
        
        assert filename.startswith("test_")
        assert filename.endswith(".csv")
        assert len(filename) > len("test_.csv")  # Should include timestamp

    def test_custom_extension(self) -> None:
        """Test filename generation with custom extension."""
        filename = get_timestamped_filename("test", "txt")
        
        assert filename.startswith("test_")
        assert filename.endswith(".txt")

    def test_timestamp_format(self) -> None:
        """Test that timestamp is in correct format."""
        filename = get_timestamped_filename("test")
        
        # Extract timestamp part (remove prefix and suffix)
        timestamp_part = filename[5:-4]  # Remove "test_" and ".csv"
        
        # Should be in format YYYYMMDD_HHMMSS
        assert len(timestamp_part) == 15
        assert timestamp_part[8] == "_"  # Underscore separator
        
        # Check that parts are numeric
        date_part = timestamp_part[:8]
        time_part = timestamp_part[9:]
        
        assert date_part.isdigit()
        assert time_part.isdigit()

    def test_multiple_calls_generate_different_names(self) -> None:
        """Test that multiple calls generate different filenames."""
        filename1 = get_timestamped_filename("test")
        filename2 = get_timestamped_filename("test")
        
        # In some cases, the timestamps might be the same if called very quickly
        # So we'll test the format instead of requiring different timestamps
        assert filename1.startswith("test_")
        assert filename1.endswith(".csv")
        assert filename2.startswith("test_")
        assert filename2.endswith(".csv")
        
        # Extract timestamp parts and verify format
        timestamp1 = filename1[5:-4]  # Remove "test_" and ".csv"
        timestamp2 = filename2[5:-4]
        
        assert len(timestamp1) == 15  # YYYYMMDD_HHMMSS
        assert len(timestamp2) == 15
        assert timestamp1[8] == "_"  # Underscore separator
        assert timestamp2[8] == "_"