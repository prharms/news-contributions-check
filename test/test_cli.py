"""Tests for the CLI module."""

import argparse
from unittest.mock import Mock, patch

import pytest

from news_contribution_check.cli import cli
from news_contribution_check.config import AppConfig


class TestCLI:
    """Test cases for CLI module."""

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_default_arguments(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with default arguments."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists and is_relative_to to return True
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_relative_to', return_value=True):
            # Mock argparse with a file argument
            with patch('sys.argv', ['script_name', 'testfile.docx']):
                cli()
            
            # Verify main was called with the file path
            mock_main.assert_called_once_with(
                file_path="data\\testfile.docx",
                output_directory="output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_custom_output_dir(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with custom output directory."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists and is_relative_to to return True
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_relative_to', return_value=True):
            # Mock argparse with custom output directory
            with patch('sys.argv', ['script_name', 'testfile.docx', '--output-dir', '/custom/output']):
                cli()
            
            # Verify main was called with custom output directory
            mock_main.assert_called_once_with(
                file_path="data\\testfile.docx",
                output_directory="/custom/output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_full_file_path(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with full file path."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists and is_relative_to to return True
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_relative_to', return_value=True):
            # Mock argparse with full file path
            with patch('sys.argv', ['script_name', 'data/testfile.docx']):
                cli()
            
            # Verify main was called with the full file path
            mock_main.assert_called_once_with(
                file_path="data\\testfile.docx",
                output_directory="output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_verbose_flag(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with verbose flag."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists and is_relative_to to return True
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_relative_to', return_value=True):
            # Mock argparse with verbose flag
            with patch('sys.argv', ['script_name', 'testfile.docx', '--verbose']):
                cli()
            
            # Verify main was called with the file path
            mock_main.assert_called_once_with(
                file_path="data\\testfile.docx",
                output_directory="output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_short_verbose_flag(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with short verbose flag."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists and is_relative_to to return True
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_relative_to', return_value=True):
            # Mock argparse with short verbose flag
            with patch('sys.argv', ['script_name', 'testfile.docx', '-v']):
                cli()
            
            # Verify main was called with the file path
            mock_main.assert_called_once_with(
                file_path="data\\testfile.docx",
                output_directory="output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_help_flag(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with help flag."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock argparse with help flag
        with patch('sys.argv', ['script_name', '--help']):
            # This should not call main() but instead show help
            with pytest.raises(SystemExit):
                cli()
        
        # Verify main was not called
        mock_main.assert_not_called()

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_app_config_creation(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test that CLI creates AppConfig instance."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists and is_relative_to to return True
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_relative_to', return_value=True):
            # Mock argparse
            with patch('sys.argv', ['script_name', 'testfile.docx']):
                cli()
            
            # Verify AppConfig was created
            mock_app_config_class.assert_called_once()

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_uses_config_properties(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test that CLI uses config properties correctly."""
        # Mock AppConfig with different values
        mock_config = Mock()
        mock_config.data_directory = "/config/data"
        mock_config.output_directory = "/config/output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists to return True (file exists)
        with patch('pathlib.Path.exists', return_value=True):
            # Mock argparse
            with patch('sys.argv', ['script_name', 'testfile.docx']):
                cli()
            
            # Verify main was called with config values
            mock_main.assert_called_once_with(
                file_path="/config/data\\testfile.docx",
                output_directory="/config/output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_argument_precedence(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test that CLI arguments take precedence over config defaults."""
        # Mock AppConfig with default values
        mock_config = Mock()
        mock_config.data_directory = "/config/data"
        mock_config.output_directory = "/config/output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists to return True (file exists)
        with patch('pathlib.Path.exists', return_value=True):
            # Mock argparse with custom output directory
            with patch('sys.argv', ['script_name', 'testfile.docx', '--output-dir', '/arg/output']):
                cli()
            
            # Verify main was called with config data directory and argument output directory
            mock_main.assert_called_once_with(
                file_path="/config/data\\testfile.docx",
                output_directory="/arg/output",
            )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_file_validation(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test that CLI validates file arguments correctly."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists to return False (file doesn't exist)
        with patch('pathlib.Path.exists', return_value=False):
            with patch('sys.argv', ['script_name', 'nonexistent.docx']):
                result = cli()
                assert result == 1  # CLI should return 1 on error
        
        # Verify main was not called
        mock_main.assert_not_called()

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_file_extension_validation(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test that CLI validates file extension correctly."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock Path.exists to return True (file exists)
        with patch('pathlib.Path.exists', return_value=True):
            with patch('sys.argv', ['script_name', 'testfile.txt']):
                result = cli()
                assert result == 1  # CLI should return 1 on error
        
        # Verify main was not called
        mock_main.assert_not_called()
