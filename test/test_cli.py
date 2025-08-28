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
        
        # Mock argparse
        with patch('sys.argv', ['script_name']):
            cli()
        
        # Verify main was called with config defaults
        mock_main.assert_called_once_with(
            data_directory="data",
            output_directory="output",
        )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_custom_arguments(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with custom arguments."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock argparse with custom arguments
        with patch('sys.argv', ['script_name', '--data-dir', '/custom/data', '--output-dir', '/custom/output']):
            cli()
        
        # Verify main was called with custom arguments
        mock_main.assert_called_once_with(
            data_directory="/custom/data",
            output_directory="/custom/output",
        )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_partial_arguments(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with partial arguments (some custom, some default)."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock argparse with only data-dir argument
        with patch('sys.argv', ['script_name', '--data-dir', '/custom/data']):
            cli()
        
        # Verify main was called with custom data-dir and default output-dir
        mock_main.assert_called_once_with(
            data_directory="/custom/data",
            output_directory="output",
        )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_with_verbose_flag(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test CLI with verbose flag (should be ignored for now)."""
        # Mock AppConfig
        mock_config = Mock()
        mock_config.data_directory = "data"
        mock_config.output_directory = "output"
        mock_app_config_class.return_value = mock_config
        
        # Mock argparse with verbose flag
        with patch('sys.argv', ['script_name', '--verbose']):
            cli()
        
        # Verify main was called with default arguments (verbose flag not yet implemented)
        mock_main.assert_called_once_with(
            data_directory="data",
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
        
        # Mock argparse with short verbose flag
        with patch('sys.argv', ['script_name', '-v']):
            cli()
        
        # Verify main was called with default arguments
        mock_main.assert_called_once_with(
            data_directory="data",
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
        
        # Mock argparse
        with patch('sys.argv', ['script_name']):
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
        
        # Mock argparse
        with patch('sys.argv', ['script_name']):
            cli()
        
        # Verify main was called with config values
        mock_main.assert_called_once_with(
            data_directory="/config/data",
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
        
        # Mock argparse with arguments that should override config
        with patch('sys.argv', ['script_name', '--data-dir', '/arg/data', '--output-dir', '/arg/output']):
            cli()
        
        # Verify main was called with argument values (not config values)
        mock_main.assert_called_once_with(
            data_directory="/arg/data",
            output_directory="/arg/output",
        )

    @patch('news_contribution_check.cli.main')
    @patch('news_contribution_check.cli.AppConfig')
    def test_cli_mixed_argument_precedence(self, mock_app_config_class: Mock, mock_main: Mock) -> None:
        """Test that CLI arguments take precedence over config defaults when mixed."""
        # Mock AppConfig with default values
        mock_config = Mock()
        mock_config.data_directory = "/config/data"
        mock_config.output_directory = "/config/output"
        mock_app_config_class.return_value = mock_config
        
        # Mock argparse with only output-dir argument
        with patch('sys.argv', ['script_name', '--output-dir', '/arg/output']):
            cli()
        
        # Verify main was called with config data-dir and argument output-dir
        mock_main.assert_called_once_with(
            data_directory="/config/data",
            output_directory="/arg/output",
        )
