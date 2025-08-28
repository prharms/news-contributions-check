"""Tests for the orchestrator service."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from news_contribution_check.claude_analyzer import ArticleAnalysis, CompanyMention
from news_contribution_check.document_processor import Article
from news_contribution_check.exceptions import (
    ClaudeAPIError,
    CSVExportError,
    DocumentProcessingError,
)
from news_contribution_check.orchestrator import (
    NewsContributionOrchestrator,
    ProcessingResult,
    ProcessingSummary,
    ResultFiles,
)


class TestNewsContributionOrchestrator:
    """Test cases for NewsContributionOrchestrator class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_document_processor = Mock()
        self.mock_claude_analyzer = Mock()
        self.mock_csv_exporter = Mock()
        self.mock_logger = Mock()
        self.mock_config = Mock()
        
        self.orchestrator = NewsContributionOrchestrator(
            document_processor=self.mock_document_processor,
            claude_analyzer=self.mock_claude_analyzer,
            csv_exporter=self.mock_csv_exporter,
            logger=self.mock_logger,
            config=self.mock_config,
        )

    def test_initialization(self) -> None:
        """Test orchestrator initialization."""
        assert self.orchestrator._document_processor is self.mock_document_processor
        assert self.orchestrator._claude_analyzer is self.mock_claude_analyzer
        assert self.orchestrator._csv_exporter is self.mock_csv_exporter
        assert self.orchestrator._logger is self.mock_logger
        assert self.orchestrator._config is self.mock_config

    def test_process_news_articles_success(self) -> None:
        """Test successful processing workflow."""
        # Setup mocks
        articles = [
            Article(title="Test 1", source="Source 1", date="2024-01-01", content="Content 1", raw_text="Raw 1"),
            Article(title="Test 2", source="Source 2", date="2024-01-02", content="Content 2", raw_text="Raw 2"),
        ]
        
        analyses = [
            ArticleAnalysis(
                article_title="Test 1",
                publication_source="Source 1",
                publication_date="2024-01-01",
                company_mentions=[CompanyMention(company_name="Company A", description="Description A")]
            ),
            ArticleAnalysis(
                article_title="Test 2",
                publication_source="Source 2",
                publication_date="2024-01-02",
                company_mentions=[]
            ),
        ]
        
        result_files = ResultFiles(
            main_results=Path("output/results.csv"),
            summary_stats=Path("output/summary.csv")
        )
        
        self.mock_document_processor.process_all_files.return_value = articles
        self.mock_claude_analyzer.analyze_articles.return_value = analyses
        self.mock_csv_exporter.export_results.return_value = result_files.main_results
        self.mock_csv_exporter.export_summary_stats.return_value = result_files.summary_stats
        
        # Execute
        result = self.orchestrator.process_news_articles()
        
        # Verify
        assert isinstance(result, ProcessingResult)
        assert result.articles == articles
        assert result.analyses == analyses
        assert result.result_files == result_files
        assert result.summary.total_articles == 2
        assert result.summary.articles_with_mentions == 1
        assert result.summary.total_mentions == 1
        assert result.summary.unique_companies == 1
        
        # Verify logging
        self.mock_logger.info.assert_any_call("Starting news contribution analysis")
        self.mock_logger.info.assert_any_call("Extracting articles from documents")
        self.mock_logger.info.assert_any_call("Extracted 2 articles")
        self.mock_logger.info.assert_any_call("Analyzing 2 articles with Claude AI")
        self.mock_logger.info.assert_any_call("Analysis complete. Found 1 company mentions")
        self.mock_logger.info.assert_any_call("Exporting results to CSV")
        self.mock_logger.info.assert_any_call("News contribution analysis completed successfully")

    def test_process_news_articles_no_articles(self) -> None:
        """Test processing when no articles are found."""
        self.mock_document_processor.process_all_files.return_value = []
        
        result = self.orchestrator.process_news_articles()
        
        assert result == ProcessingResult.empty()
        self.mock_logger.warning.assert_called_with("No articles found to process")

    def test_process_news_articles_with_custom_directories(self) -> None:
        """Test processing with custom data and output directories."""
        data_dir = Path("/custom/data")
        output_dir = Path("/custom/output")
        
        articles = [Article(title="Test", source="Source", date="2024-01-01", content="Content", raw_text="Raw")]
        analyses = [
            ArticleAnalysis(
                article_title="Test",
                publication_source="Source",
                publication_date="2024-01-01",
                company_mentions=[]
            )
        ]
        
        self.mock_document_processor.process_all_files.return_value = articles
        self.mock_claude_analyzer.analyze_articles.return_value = analyses
        self.mock_csv_exporter.export_results.return_value = Path("output/results.csv")
        self.mock_csv_exporter.export_summary_stats.return_value = Path("output/summary.csv")
        
        # For custom directories, the orchestrator creates new instances internally
        # We need to mock the imports inside the methods where they're used
        with patch('news_contribution_check.document_processor.DocumentProcessor') as mock_processor_class, \
             patch('news_contribution_check.csv_exporter.CSVExporter') as mock_exporter_class:
            
            mock_processor_instance = Mock()
            mock_processor_instance.process_all_files.return_value = articles
            mock_processor_class.return_value = mock_processor_instance
            
            mock_exporter_instance = Mock()
            mock_exporter_instance.export_results.return_value = Path("output/results.csv")
            mock_exporter_instance.export_summary_stats.return_value = Path("output/summary.csv")
            mock_exporter_class.return_value = mock_exporter_instance
            
            result = self.orchestrator.process_news_articles(data_dir, output_dir)
            
            # Verify new instances were created with correct directories
            mock_processor_class.assert_called_once_with(data_dir)
            mock_exporter_class.assert_called_once_with(output_dir)

    def test_extract_articles_success(self) -> None:
        """Test successful article extraction."""
        articles = [Article(title="Test", source="Source", date="2024-01-01", content="Content", raw_text="Raw")]
        self.mock_document_processor.process_all_files.return_value = articles
        
        result = self.orchestrator._extract_articles(None)
        
        assert result == articles
        self.mock_logger.info.assert_called_with("Extracted 1 articles")

    def test_extract_articles_failure(self) -> None:
        """Test article extraction failure."""
        self.mock_document_processor.process_all_files.side_effect = Exception("Processing failed")
        
        with pytest.raises(DocumentProcessingError, match="Failed to extract articles"):
            self.orchestrator._extract_articles(None)

    def test_analyze_articles_success(self) -> None:
        """Test successful article analysis."""
        articles = [Article(title="Test", source="Source", date="2024-01-01", content="Content", raw_text="Raw")]
        analyses = [
            ArticleAnalysis(
                article_title="Test",
                publication_source="Source",
                publication_date="2024-01-01",
                company_mentions=[CompanyMention(company_name="Company", description="Description")]
            )
        ]
        
        self.mock_claude_analyzer.analyze_articles.return_value = analyses
        
        result = self.orchestrator._analyze_articles(articles)
        
        assert result == analyses
        self.mock_logger.info.assert_called_with("Analysis complete. Found 1 company mentions")

    def test_analyze_articles_failure(self) -> None:
        """Test article analysis failure."""
        articles = [Article(title="Test", source="Source", date="2024-01-01", content="Content", raw_text="Raw")]
        self.mock_claude_analyzer.analyze_articles.side_effect = Exception("Analysis failed")
        
        with pytest.raises(ClaudeAPIError, match="Failed to analyze articles"):
            self.orchestrator._analyze_articles(articles)

    def test_export_results_success(self) -> None:
        """Test successful results export."""
        analyses = [
            ArticleAnalysis(
                article_title="Test",
                publication_source="Source",
                publication_date="2024-01-01",
                company_mentions=[]
            )
        ]
        
        self.mock_csv_exporter.export_results.return_value = Path("output/results.csv")
        self.mock_csv_exporter.export_summary_stats.return_value = Path("output/summary.csv")
        
        result = self.orchestrator._export_results(analyses, None)
        
        assert isinstance(result, ResultFiles)
        assert result.main_results == Path("output/results.csv")
        assert result.summary_stats == Path("output/summary.csv")

    def test_export_results_failure(self) -> None:
        """Test results export failure."""
        analyses = [
            ArticleAnalysis(
                article_title="Test",
                publication_source="Source",
                publication_date="2024-01-01",
                company_mentions=[]
            )
        ]
        
        self.mock_csv_exporter.export_results.side_effect = Exception("Export failed")
        
        with pytest.raises(CSVExportError, match="Failed to export results"):
            self.orchestrator._export_results(analyses, None)

    def test_generate_summary(self) -> None:
        """Test summary generation."""
        analyses = [
            ArticleAnalysis(
                article_title="Test 1",
                publication_source="Source 1",
                publication_date="2024-01-01",
                company_mentions=[
                    CompanyMention(company_name="Company A", description="Description A"),
                    CompanyMention(company_name="Company B", description="Description B")
                ]
            ),
            ArticleAnalysis(
                article_title="Test 2",
                publication_source="Source 2",
                publication_date="2024-01-02",
                company_mentions=[CompanyMention(company_name="Company A", description="Description A")]
            ),
            ArticleAnalysis(
                article_title="Test 3",
                publication_source="Source 3",
                publication_date="2024-01-03",
                company_mentions=[]
            ),
        ]
        
        summary = self.orchestrator._generate_summary(analyses)
        
        assert summary.total_articles == 3
        assert summary.articles_with_mentions == 2
        assert summary.total_mentions == 3
        assert summary.unique_companies == 2  # Company A and Company B (case insensitive)

    def test_process_news_articles_exception_handling(self) -> None:
        """Test exception handling in main processing method."""
        self.mock_document_processor.process_all_files.side_effect = Exception("Unexpected error")
        
        with pytest.raises(Exception, match="Unexpected error"):
            self.orchestrator.process_news_articles()
        
        self.mock_logger.error.assert_called_with("News contribution analysis failed: Failed to extract articles: Unexpected error")


class TestProcessingResult:
    """Test cases for ProcessingResult class."""

    def test_initialization(self) -> None:
        """Test ProcessingResult initialization."""
        articles = [Mock()]
        analyses = [Mock()]
        result_files = ResultFiles(Path("results.csv"), Path("summary.csv"))
        summary = ProcessingSummary(1, 1, 1, 1)
        
        result = ProcessingResult(articles, analyses, result_files, summary)
        
        assert result.articles == articles
        assert result.analyses == analyses
        assert result.result_files == result_files
        assert result.summary == summary

    def test_empty_class_method(self) -> None:
        """Test empty ProcessingResult creation."""
        result = ProcessingResult.empty()
        
        assert result.articles == []
        assert result.analyses == []
        assert result.result_files == ResultFiles.empty()
        assert result.summary == ProcessingSummary.empty()


class TestResultFiles:
    """Test cases for ResultFiles class."""

    def test_initialization(self) -> None:
        """Test ResultFiles initialization."""
        main_results = Path("results.csv")
        summary_stats = Path("summary.csv")
        
        result_files = ResultFiles(main_results, summary_stats)
        
        assert result_files.main_results == main_results
        assert result_files.summary_stats == summary_stats

    def test_empty_class_method(self) -> None:
        """Test empty ResultFiles creation."""
        result_files = ResultFiles.empty()
        
        assert result_files.main_results == Path("")
        assert result_files.summary_stats == Path("")


class TestProcessingSummary:
    """Test cases for ProcessingSummary class."""

    def test_initialization(self) -> None:
        """Test ProcessingSummary initialization."""
        summary = ProcessingSummary(
            total_articles=10,
            articles_with_mentions=5,
            total_mentions=15,
            unique_companies=8
        )
        
        assert summary.total_articles == 10
        assert summary.articles_with_mentions == 5
        assert summary.total_mentions == 15
        assert summary.unique_companies == 8

    def test_empty_class_method(self) -> None:
        """Test empty ProcessingSummary creation."""
        summary = ProcessingSummary.empty()
        
        assert summary.total_articles == 0
        assert summary.articles_with_mentions == 0
        assert summary.total_mentions == 0
        assert summary.unique_companies == 0
