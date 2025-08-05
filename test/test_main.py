"""Tests for main module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.claude_analyzer import ArticleAnalysis, CompanyMention
from src.document_processor import Article
from src.main import main


class TestMain:
    """Test cases for main function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_data_dir = Path(tempfile.mkdtemp())
        self.temp_output_dir = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_data_dir)
        shutil.rmtree(self.temp_output_dir)

    @patch('src.main.DocumentProcessor')
    @patch('src.main.ClaudeAnalyzer')
    @patch('src.main.CSVExporter')
    @patch('builtins.print')
    def test_main_success(
        self,
        mock_print: Mock,
        mock_csv_exporter: Mock,
        mock_claude_analyzer: Mock,
        mock_document_processor: Mock
    ) -> None:
        """Test successful main execution."""
        # Mock document processor
        mock_doc_processor = Mock()
        mock_articles = [
            Article(
                title="Test Article",
                source="Test Source",
                date="2024-01-15",
                content="Test content",
                raw_text="Raw text"
            )
        ]
        mock_doc_processor.process_all_files.return_value = mock_articles
        mock_doc_processor.find_docx_files.return_value = [Path("test.docx")]
        mock_document_processor.return_value = mock_doc_processor

        # Mock Claude analyzer
        mock_analyzer = Mock()
        mock_analyses = [
            ArticleAnalysis(
                article_title="Test Article",
                publication_source="Test Source",
                publication_date="2024-01-15",
                company_mentions=[
                    CompanyMention(company_name="Apple Inc.", description="Tech company")
                ]
            )
        ]
        mock_analyzer.analyze_articles.return_value = mock_analyses
        mock_claude_analyzer.return_value = mock_analyzer

        # Mock CSV exporter
        mock_exporter = Mock()
        mock_exporter.export_results.return_value = Path("output/results.csv")
        mock_exporter.export_summary_stats.return_value = Path("output/summary.csv")
        mock_csv_exporter.return_value = mock_exporter

        # Run main function
        main(
            data_directory=str(self.temp_data_dir),
            output_directory=str(self.temp_output_dir),
            api_key="test-key"
        )

        # Verify calls
        mock_document_processor.assert_called_once_with(self.temp_data_dir)
        mock_claude_analyzer.assert_called_once_with("test-key")
        mock_csv_exporter.assert_called_once_with(self.temp_output_dir)

        mock_doc_processor.process_all_files.assert_called_once()
        mock_analyzer.analyze_articles.assert_called_once_with(mock_articles)
        mock_exporter.export_results.assert_called_once_with(mock_analyses)
        mock_exporter.export_summary_stats.assert_called_once_with(mock_analyses)

        # Check that success messages were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Processing Complete!" in call for call in print_calls)
        assert any("Total articles processed: 1" in call for call in print_calls)
        assert any("Total company mentions found: 1" in call for call in print_calls)

    @patch('src.main.DocumentProcessor')
    @patch('builtins.print')
    def test_main_no_articles(
        self,
        mock_print: Mock,
        mock_document_processor: Mock
    ) -> None:
        """Test main execution with no articles found."""
        # Mock document processor returning no articles
        mock_doc_processor = Mock()
        mock_doc_processor.process_all_files.return_value = []
        mock_document_processor.return_value = mock_doc_processor

        # Run main function
        main(
            data_directory=str(self.temp_data_dir),
            output_directory=str(self.temp_output_dir),
            api_key="test-key"
        )

        # Verify that function returns early with no articles message
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("No articles found. Exiting." in call for call in print_calls)

    @patch('src.main.DocumentProcessor')
    @patch('builtins.print')
    def test_main_document_processor_failure(
        self,
        mock_print: Mock,
        mock_document_processor: Mock
    ) -> None:
        """Test main execution with document processor failure."""
        # Mock document processor raising exception
        mock_doc_processor = Mock()
        mock_doc_processor.process_all_files.side_effect = Exception("Document processing failed")
        mock_document_processor.return_value = mock_doc_processor

        # Run main function and expect SystemExit
        with pytest.raises(SystemExit):
            main(
                data_directory=str(self.temp_data_dir),
                output_directory=str(self.temp_output_dir),
                api_key="test-key"
            )

        # Check error message was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Error during processing: Document processing failed" in call for call in print_calls)

    @patch('src.main.DocumentProcessor')
    @patch('src.main.ClaudeAnalyzer')
    @patch('builtins.print')
    def test_main_claude_analyzer_failure(
        self,
        mock_print: Mock,
        mock_claude_analyzer: Mock,
        mock_document_processor: Mock
    ) -> None:
        """Test main execution with Claude analyzer failure."""
        # Mock document processor
        mock_doc_processor = Mock()
        mock_articles = [
            Article(
                title="Test Article",
                source="Test Source",
                date="2024-01-15",
                content="Test content",
                raw_text="Raw text"
            )
        ]
        mock_doc_processor.process_all_files.return_value = mock_articles
        mock_doc_processor.find_docx_files.return_value = [Path("test.docx")]
        mock_document_processor.return_value = mock_doc_processor

        # Mock Claude analyzer raising exception
        mock_analyzer = Mock()
        mock_analyzer.analyze_articles.side_effect = Exception("Claude analysis failed")
        mock_claude_analyzer.return_value = mock_analyzer

        # Run main function and expect SystemExit
        with pytest.raises(SystemExit):
            main(
                data_directory=str(self.temp_data_dir),
                output_directory=str(self.temp_output_dir),
                api_key="test-key"
            )

        # Check error message was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Error during processing: Claude analysis failed" in call for call in print_calls)

    @patch('src.main.DocumentProcessor')
    @patch('src.main.ClaudeAnalyzer')
    @patch('src.main.CSVExporter')
    @patch('builtins.print')
    def test_main_csv_exporter_failure(
        self,
        mock_print: Mock,
        mock_csv_exporter: Mock,
        mock_claude_analyzer: Mock,
        mock_document_processor: Mock
    ) -> None:
        """Test main execution with CSV exporter failure."""
        # Mock document processor
        mock_doc_processor = Mock()
        mock_articles = [
            Article(
                title="Test Article",
                source="Test Source",
                date="2024-01-15",
                content="Test content",
                raw_text="Raw text"
            )
        ]
        mock_doc_processor.process_all_files.return_value = mock_articles
        mock_doc_processor.find_docx_files.return_value = [Path("test.docx")]
        mock_document_processor.return_value = mock_doc_processor

        # Mock Claude analyzer
        mock_analyzer = Mock()
        mock_analyses = [
            ArticleAnalysis(
                article_title="Test Article",
                publication_source="Test Source",
                publication_date="2024-01-15",
                company_mentions=[]
            )
        ]
        mock_analyzer.analyze_articles.return_value = mock_analyses
        mock_claude_analyzer.return_value = mock_analyzer

        # Mock CSV exporter raising exception
        mock_exporter = Mock()
        mock_exporter.export_results.side_effect = Exception("CSV export failed")
        mock_csv_exporter.return_value = mock_exporter

        # Run main function and expect SystemExit
        with pytest.raises(SystemExit):
            main(
                data_directory=str(self.temp_data_dir),
                output_directory=str(self.temp_output_dir),
                api_key="test-key"
            )

        # Check error message was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("Error during processing: CSV export failed" in call for call in print_calls)

    @patch('src.main.DocumentProcessor')
    @patch('src.main.ClaudeAnalyzer')
    @patch('src.main.CSVExporter')
    @patch('builtins.print')
    def test_main_with_default_parameters(
        self,
        mock_print: Mock,
        mock_csv_exporter: Mock,
        mock_claude_analyzer: Mock,
        mock_document_processor: Mock
    ) -> None:
        """Test main execution with default parameters."""
        # Mock all components for successful execution
        mock_doc_processor = Mock()
        mock_articles = [
            Article(
                title="Test Article",
                source="Test Source",
                date="2024-01-15",
                content="Test content",
                raw_text="Raw text"
            )
        ]
        mock_doc_processor.process_all_files.return_value = mock_articles
        mock_doc_processor.find_docx_files.return_value = [Path("test.docx")]
        mock_document_processor.return_value = mock_doc_processor

        mock_analyzer = Mock()
        mock_analyses = [
            ArticleAnalysis(
                article_title="Test Article",
                publication_source="Test Source",
                publication_date="2024-01-15",
                company_mentions=[]
            )
        ]
        mock_analyzer.analyze_articles.return_value = mock_analyses
        mock_claude_analyzer.return_value = mock_analyzer

        mock_exporter = Mock()
        mock_exporter.export_results.return_value = Path("output/results.csv")
        mock_exporter.export_summary_stats.return_value = Path("output/summary.csv")
        mock_csv_exporter.return_value = mock_exporter

        # Run main function with defaults
        main()

        # Verify default parameters were used
        mock_document_processor.assert_called_once_with(Path("data"))
        mock_claude_analyzer.assert_called_once_with(None)  # Uses env var
        mock_csv_exporter.assert_called_once_with(Path("output"))