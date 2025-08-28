"""Tests for logging configuration utilities."""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from news_contribution_check.logging_config import (
    setup_logging,
    get_logger,
    set_log_level,
    enable_debug_logging,
    enable_verbose_logging,
    enable_quiet_logging,
)


class TestLoggingConfig:
    """Test cases for logging configuration utilities."""

    def test_setup_logging_default(self) -> None:
        """Test default logging setup."""
        logger = setup_logging()
        
        assert logger.name == "news_contribution_check"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 2  # Console and file handlers
        assert not logger.propagate

    def test_setup_logging_debug_level(self) -> None:
        """Test logging setup with DEBUG level."""
        logger = setup_logging(level="DEBUG")
        
        assert logger.level == logging.DEBUG
        # Console handler should be at DEBUG level
        console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
        assert console_handler.level == logging.DEBUG

    def test_setup_logging_console_only(self) -> None:
        """Test logging setup with console only."""
        logger = setup_logging(log_to_file=False, log_to_console=True)
        
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_file_only(self) -> None:
        """Test logging setup with file only."""
        logger = setup_logging(log_to_file=True, log_to_console=False)
        
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_setup_logging_custom_directory(self) -> None:
        """Test logging setup with custom log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            logger = setup_logging(log_dir=log_dir)
            
            # Check that log file was created
            log_file = log_dir / "news_contribution_check.log"
            assert log_file.exists()
            
            # Close all handlers to prevent file locking issues
            for handler in logger.handlers:
                handler.close()

    def test_setup_logging_json_format(self) -> None:
        """Test logging setup with JSON format."""
        logger = setup_logging(json_format=True)
        
        # Check that handlers have JSON formatters
        for handler in logger.handlers:
            assert "JsonFormatter" in handler.formatter.__class__.__name__

    def test_get_logger_default(self) -> None:
        """Test getting default logger."""
        logger = get_logger()
        
        assert logger.name == "news_contribution_check"

    def test_get_logger_custom_name(self) -> None:
        """Test getting logger with custom name."""
        logger = get_logger("custom.logger")
        
        assert logger.name == "custom.logger"

    def test_set_log_level(self) -> None:
        """Test setting log level."""
        logger = setup_logging()
        set_log_level("WARNING")
        
        assert logger.level == logging.WARNING
        # Console handler should also be updated
        console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
        assert console_handler.level == logging.WARNING

    def test_enable_debug_logging(self) -> None:
        """Test enabling debug logging."""
        logger = setup_logging()
        enable_debug_logging()
        
        assert logger.level == logging.DEBUG

    def test_enable_verbose_logging(self) -> None:
        """Test enabling verbose logging."""
        logger = setup_logging()
        enable_verbose_logging()
        
        assert logger.level == logging.INFO

    def test_enable_quiet_logging(self) -> None:
        """Test enabling quiet logging."""
        logger = setup_logging()
        enable_quiet_logging()
        
        assert logger.level == logging.WARNING

    def test_setup_logging_prevents_duplicates(self) -> None:
        """Test that setup_logging prevents duplicate handlers."""
        logger1 = setup_logging()
        logger2 = setup_logging()
        
        # Should be the same logger instance
        assert logger1 is logger2
        # Should have the same number of handlers (not doubled)
        assert len(logger1.handlers) == 2

    def test_logging_with_extra_fields(self) -> None:
        """Test logging with extra structured fields."""
        logger = setup_logging()
        
        # Test logging with extra fields
        logger.info("Test message", extra={
            'operation': 'test_operation',
            'status': 'success',
            'test_field': 'test_value'
        })
        
        # The message should be logged without error
        assert True  # If we get here, no exception was raised

    def test_json_formatter_with_extra_fields(self) -> None:
        """Test JSON formatter with extra fields."""
        logger = setup_logging(json_format=True)
        
        # Test logging with extra fields
        logger.info("Test message", extra={
            'operation': 'test_operation',
            'status': 'success',
            'error_type': 'TestError',
            'error_message': 'Test error message'
        })
        
        # The message should be logged without error
        assert True  # If we get here, no exception was raised
