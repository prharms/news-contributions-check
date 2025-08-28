"""Tests for the Container class."""

import logging
import os
from pathlib import Path
from unittest.mock import Mock, patch, ANY

import pytest

from news_contribution_check.config import AppConfig
from news_contribution_check.container import Container
from news_contribution_check.exceptions import ConfigurationError


class TestContainer:
    """Test cases for Container class."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_initialization_with_default_config(self) -> None:
        """Test container initialization with default configuration."""
        container = Container()
        
        assert isinstance(container.config, AppConfig)
        assert isinstance(container.logger, logging.Logger)
        assert container.logger.name == "news_contribution_check"

    def test_initialization_with_custom_config(self) -> None:
        """Test container initialization with custom configuration."""
        config = AppConfig()
        container = Container(config=config)
        
        assert container.config is config

    @patch('news_contribution_check.container.load_dotenv')
    def test_load_config_calls_load_dotenv(self, mock_load_dotenv: Mock) -> None:
        """Test that _load_config calls load_dotenv."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            container = Container()
            mock_load_dotenv.assert_called_once()

    def test_setup_logging_creates_logger(self) -> None:
        """Test that _setup_logging creates a proper logger."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            container = Container()
            
            logger = container.logger
            assert logger.level == logging.INFO
            assert len(logger.handlers) == 2  # Console and file handlers
            assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
            assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    def test_setup_logging_prevents_duplicate_handlers(self) -> None:
        """Test that _setup_logging prevents duplicate handlers."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            container1 = Container()
            container2 = Container()
            
            # Both should use the same logger instance
            assert container1.logger is container2.logger
            assert len(container1.logger.handlers) == 2  # Console and file handlers

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_claude_analyzer_creates_instance(self) -> None:
        """Test that get_claude_analyzer creates a ClaudeAnalyzer instance."""
        with patch('news_contribution_check.container.ClaudeAnalyzer') as mock_claude:
            mock_instance = Mock()
            mock_claude.return_value = mock_instance
            
            container = Container()
            analyzer = container.get_claude_analyzer()
            
            assert analyzer is mock_instance
            mock_claude.assert_called_once_with(api_key='test-api-key', config=ANY)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_claude_analyzer_caches_instance(self) -> None:
        """Test that get_claude_analyzer caches the instance."""
        with patch('news_contribution_check.container.ClaudeAnalyzer') as mock_claude:
            mock_instance = Mock()
            mock_claude.return_value = mock_instance
            
            container = Container()
            analyzer1 = container.get_claude_analyzer()
            analyzer2 = container.get_claude_analyzer()
            
            assert analyzer1 is analyzer2
            mock_claude.assert_called_once()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_document_processor_creates_instance(self) -> None:
        """Test that get_document_processor creates a DocumentProcessor instance."""
        with patch('news_contribution_check.container.DocumentProcessor') as mock_processor:
            mock_instance = Mock()
            mock_processor.return_value = mock_instance
            
            container = Container()
            processor = container.get_document_processor()
            
            assert processor is mock_instance
            mock_processor.assert_called_once_with(Path("data"), config=ANY)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_document_processor_with_custom_directory(self) -> None:
        """Test that get_document_processor uses custom directory."""
        custom_dir = Path("/custom/data")
        
        with patch('news_contribution_check.container.DocumentProcessor') as mock_processor:
            mock_instance = Mock()
            mock_processor.return_value = mock_instance
            
            container = Container()
            processor = container.get_document_processor(custom_dir)
            
            assert processor is mock_instance
            mock_processor.assert_called_once_with(custom_dir, config=ANY)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_csv_exporter_creates_instance(self) -> None:
        """Test that get_csv_exporter creates a CSVExporter instance."""
        with patch('news_contribution_check.container.CSVExporter') as mock_exporter:
            mock_instance = Mock()
            mock_exporter.return_value = mock_instance
            
            container = Container()
            exporter = container.get_csv_exporter()
            
            assert exporter is mock_instance
            mock_exporter.assert_called_once_with(Path("output"))

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_get_csv_exporter_with_custom_directory(self) -> None:
        """Test that get_csv_exporter uses custom directory."""
        custom_dir = Path("/custom/output")
        
        with patch('news_contribution_check.container.CSVExporter') as mock_exporter:
            mock_instance = Mock()
            mock_exporter.return_value = mock_instance
            
            container = Container()
            exporter = container.get_csv_exporter(custom_dir)
            
            assert exporter is mock_instance
            mock_exporter.assert_called_once_with(custom_dir)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_reset_clears_cached_instances(self) -> None:
        """Test that reset clears all cached instances."""
        with patch('news_contribution_check.container.ClaudeAnalyzer') as mock_claude, \
             patch('news_contribution_check.container.DocumentProcessor') as mock_processor, \
             patch('news_contribution_check.container.CSVExporter') as mock_exporter:
            
            mock_claude.return_value = Mock()
            mock_processor.return_value = Mock()
            mock_exporter.return_value = Mock()
            
            container = Container()
            
            # Create instances
            container.get_claude_analyzer()
            container.get_document_processor()
            container.get_csv_exporter()
            
            # Reset
            container.reset()
            
            # Create new instances
            container.get_claude_analyzer()
            container.get_document_processor()
            container.get_csv_exporter()
            
            # Should be called twice (once before reset, once after)
            assert mock_claude.call_count == 2
            assert mock_processor.call_count == 2
            assert mock_exporter.call_count == 2

    def test_missing_api_key_raises_error(self) -> None:
        """Test that missing API key raises ConfigurationError."""
        # The error is raised when get_api_key() is called, not during initialization
        with patch('news_contribution_check.container.load_dotenv'), \
             patch.dict('os.environ', {}, clear=True):
            container = Container()
            with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY environment variable is required"):
                container._config.get_api_key()
