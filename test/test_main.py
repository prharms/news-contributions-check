"""Tests for main module."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from news_contribution_check.main import main
from news_contribution_check.orchestrator import ProcessingResult, ResultFiles, ProcessingSummary


class TestMain:
    """Test cases for main module."""

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_success(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test successful main execution."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_result = Mock()
        mock_result.summary.total_articles = 5
        mock_result.summary.articles_with_mentions = 3
        mock_result.summary.total_mentions = 10
        mock_result.summary.unique_companies = 7
        mock_result.result_files.main_results = Path("output/results.csv")
        mock_result.result_files.summary_stats = Path("output/summary.csv")
        mock_orchestrator.process_news_articles.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main
        main()
        
        # Verify orchestrator was created and called
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.process_news_articles.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_no_articles(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with no articles."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_result = Mock()
        mock_result.summary.total_articles = 0
        mock_result.summary.articles_with_mentions = 0
        mock_result.summary.total_mentions = 0
        mock_result.summary.unique_companies = 0
        mock_result.result_files.main_results = Path("")
        mock_result.result_files.summary_stats = Path("")
        mock_orchestrator.process_news_articles.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main
        main()
        
        # Verify orchestrator was called
        mock_orchestrator.process_news_articles.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_document_processor_failure(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with document processor failure."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.process_news_articles.side_effect = Exception("Document processing failed")
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main and expect it to exit
        with pytest.raises(SystemExit):
            main()
        
        # Verify orchestrator was called
        mock_orchestrator.process_news_articles.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_claude_analyzer_failure(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with Claude analyzer failure."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.process_news_articles.side_effect = Exception("Claude analysis failed")
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main and expect it to exit
        with pytest.raises(SystemExit):
            main()
        
        # Verify orchestrator was called
        mock_orchestrator.process_news_articles.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_csv_exporter_failure(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with CSV exporter failure."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.process_news_articles.side_effect = Exception("CSV export failed")
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main and expect it to exit
        with pytest.raises(SystemExit):
            main()
        
        # Verify orchestrator was called
        mock_orchestrator.process_news_articles.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_with_default_parameters(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with default parameters."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_result = Mock()
        mock_result.summary.total_articles = 1
        mock_result.summary.articles_with_mentions = 1
        mock_result.summary.total_mentions = 1
        mock_result.summary.unique_companies = 1
        mock_result.result_files.main_results = Path("output/results.csv")
        mock_result.result_files.summary_stats = Path("output/summary.csv")
        mock_orchestrator.process_news_articles.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main with default parameters
        main(file_path=None, output_directory=None)
        
        # Verify orchestrator was called with None values (which get converted to Path objects)
        mock_orchestrator.process_news_articles.assert_called_once_with(None, None)

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_with_custom_parameters(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with custom parameters."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_result = Mock()
        mock_result.summary.total_articles = 1
        mock_result.summary.articles_with_mentions = 1
        mock_result.summary.total_mentions = 1
        mock_result.summary.unique_companies = 1
        mock_result.result_files.main_results = Path("custom/output/results.csv")
        mock_result.result_files.summary_stats = Path("custom/output/summary.csv")
        mock_orchestrator.process_news_articles.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main with custom parameters
        main(file_path="/custom/data/testfile.docx", output_directory="/custom/output")
        
        # Verify orchestrator was called with Path objects
        mock_orchestrator.process_news_articles.assert_called_once_with(Path("/custom/data/testfile.docx"), Path("/custom/output"))

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_unexpected_error(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test main execution with unexpected error."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.process_news_articles.side_effect = RuntimeError("Unexpected error")
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main and expect it to exit
        with pytest.raises(SystemExit):
            main()
        
        # Verify orchestrator was called
        mock_orchestrator.process_news_articles.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_container_creation(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test that main creates container properly."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_container.get_document_processor.return_value = Mock()
        mock_container.get_claude_analyzer.return_value = Mock()
        mock_container.get_csv_exporter.return_value = Mock()
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_result = Mock()
        mock_result.summary.total_articles = 1
        mock_result.summary.articles_with_mentions = 1
        mock_result.summary.total_mentions = 1
        mock_result.summary.unique_companies = 1
        mock_result.result_files.main_results = Path("output/results.csv")
        mock_result.result_files.summary_stats = Path("output/summary.csv")
        mock_orchestrator.process_news_articles.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main
        main()
        
        # Verify container was created
        mock_container_class.assert_called_once()
        
        # Verify container methods were called to get dependencies
        mock_container.get_document_processor.assert_called_once()
        mock_container.get_claude_analyzer.assert_called_once()
        mock_container.get_csv_exporter.assert_called_once()

    @patch('news_contribution_check.main.Container')
    @patch('news_contribution_check.main.NewsContributionOrchestrator')
    def test_main_orchestrator_creation(self, mock_orchestrator_class: Mock, mock_container_class: Mock) -> None:
        """Test that main creates orchestrator with correct dependencies."""
        # Mock container and orchestrator
        mock_container = Mock()
        mock_container.config = Mock()
        mock_container.logger = Mock()
        mock_document_processor = Mock()
        mock_claude_analyzer = Mock()
        mock_csv_exporter = Mock()
        mock_container.get_document_processor.return_value = mock_document_processor
        mock_container.get_claude_analyzer.return_value = mock_claude_analyzer
        mock_container.get_csv_exporter.return_value = mock_csv_exporter
        mock_container_class.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_result = Mock()
        mock_result.summary.total_articles = 1
        mock_result.summary.articles_with_mentions = 1
        mock_result.summary.total_mentions = 1
        mock_result.summary.unique_companies = 1
        mock_result.result_files.main_results = Path("output/results.csv")
        mock_result.result_files.summary_stats = Path("output/summary.csv")
        mock_orchestrator.process_news_articles.return_value = mock_result
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Call main
        main()
        
        # Verify orchestrator was created with correct dependencies
        mock_orchestrator_class.assert_called_once_with(
            document_processor=mock_document_processor,
            claude_analyzer=mock_claude_analyzer,
            csv_exporter=mock_csv_exporter,
            logger=mock_container.logger,
            config=mock_container.config,
        )