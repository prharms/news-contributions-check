"""Main orchestrator service for the news contribution check application."""

from pathlib import Path
from typing import List, Optional

from .claude_analyzer import ArticleAnalysis
from .document_processor import Article
from .exceptions import DocumentProcessingError, ClaudeAPIError, CSVExportError
from .interfaces import (
    DocumentProcessorProtocol,
    ClaudeAnalyzerProtocol,
    CSVExporterProtocol,
    LoggerProtocol,
    ConfigurationProvider,
)


class NewsContributionOrchestrator:
    """Main orchestrator that coordinates the entire news contribution analysis workflow."""
    
    def __init__(
        self,
        document_processor: DocumentProcessorProtocol,
        claude_analyzer: ClaudeAnalyzerProtocol,
        csv_exporter: CSVExporterProtocol,
        logger: LoggerProtocol,
        config: ConfigurationProvider,
    ) -> None:
        """Initialize the orchestrator with its dependencies.
        
        Args:
            document_processor: Component for processing .docx files
            claude_analyzer: Component for AI analysis
            csv_exporter: Component for CSV export
            logger: Logger for application events
            config: Configuration provider
        """
        self._document_processor = document_processor
        self._claude_analyzer = claude_analyzer
        self._csv_exporter = csv_exporter
        self._logger = logger
        self._config = config
    
    def process_news_articles(
        self,
        data_directory: Optional[Path] = None,
        output_directory: Optional[Path] = None,
    ) -> "ProcessingResult":
        """Process news articles and extract company mentions.
        
        Args:
            data_directory: Directory containing .docx files. If None, uses config default.
            output_directory: Directory to save results. If None, uses config default.
            
        Returns:
            ProcessingResult containing analysis results and file paths
            
        Raises:
            DocumentProcessingError: If document processing fails
            ClaudeAPIError: If AI analysis fails
            CSVExportError: If CSV export fails
        """
        try:
            self._logger.info("Starting news contribution analysis")
            
            # Step 1: Extract articles from documents
            articles = self._extract_articles(data_directory)
            if not articles:
                self._logger.warning("No articles found to process")
                return ProcessingResult.empty()
            
            # Step 2: Analyze articles with Claude AI
            analyses = self._analyze_articles(articles)
            
            # Step 3: Export results to CSV
            result_files = self._export_results(analyses, output_directory)
            
            # Step 4: Generate summary
            summary = self._generate_summary(analyses)
            
            self._logger.info("News contribution analysis completed successfully")
            
            return ProcessingResult(
                articles=articles,
                analyses=analyses,
                result_files=result_files,
                summary=summary,
            )
            
        except Exception as e:
            self._logger.error(f"News contribution analysis failed: {e}")
            raise
    
    def _extract_articles(self, data_directory: Optional[Path]) -> List[Article]:
        """Extract articles from .docx files.
        
        Args:
            data_directory: Directory containing .docx files
            
        Returns:
            List of extracted articles
            
        Raises:
            DocumentProcessingError: If extraction fails
        """
        try:
            self._logger.info("Extracting articles from documents")
            
            if data_directory:
                # Create a new processor instance for the specified directory
                from .document_processor import DocumentProcessor
                processor = DocumentProcessor(data_directory)
                articles = processor.process_all_files()
            else:
                articles = self._document_processor.process_all_files()
            
            self._logger.info(f"Extracted {len(articles)} articles")
            return articles
            
        except Exception as e:
            raise DocumentProcessingError(
                f"Failed to extract articles: {e}",
                cause=e
            )
    
    def _analyze_articles(self, articles: List[Article]) -> List[ArticleAnalysis]:
        """Analyze articles using Claude AI.
        
        Args:
            articles: List of articles to analyze
            
        Returns:
            List of analysis results
            
        Raises:
            ClaudeAPIError: If analysis fails
        """
        try:
            self._logger.info(f"Analyzing {len(articles)} articles with Claude AI")
            
            analyses = self._claude_analyzer.analyze_articles(articles)
            
            total_mentions = sum(len(analysis.company_mentions) for analysis in analyses)
            self._logger.info(f"Analysis complete. Found {total_mentions} company mentions")
            
            return analyses
            
        except Exception as e:
            raise ClaudeAPIError(
                f"Failed to analyze articles: {e}",
                cause=e
            )
    
    def _export_results(
        self, 
        analyses: List[ArticleAnalysis], 
        output_directory: Optional[Path]
    ) -> "ResultFiles":
        """Export analysis results to CSV files.
        
        Args:
            analyses: List of analysis results
            output_directory: Directory to save results
            
        Returns:
            ResultFiles containing paths to exported files
            
        Raises:
            CSVExportError: If export fails
        """
        try:
            self._logger.info("Exporting results to CSV")
            
            if output_directory:
                # Create a new exporter instance for the specified directory
                from .csv_exporter import CSVExporter
                exporter = CSVExporter(output_directory)
            else:
                exporter = self._csv_exporter
            
            main_csv_path = exporter.export_results(analyses)
            summary_csv_path = exporter.export_summary_stats(analyses)
            
            self._logger.info(f"Results exported to {main_csv_path}")
            self._logger.info(f"Summary exported to {summary_csv_path}")
            
            return ResultFiles(
                main_results=main_csv_path,
                summary_stats=summary_csv_path,
            )
            
        except Exception as e:
            raise CSVExportError(
                f"Failed to export results: {e}",
                cause=e
            )
    
    def _generate_summary(self, analyses: List[ArticleAnalysis]) -> "ProcessingSummary":
        """Generate summary statistics from analysis results.
        
        Args:
            analyses: List of analysis results
            
        Returns:
            ProcessingSummary with statistics
        """
        total_articles = len(analyses)
        total_mentions = sum(len(analysis.company_mentions) for analysis in analyses)
        articles_with_mentions = sum(
            1 for analysis in analyses if analysis.company_mentions
        )
        
        # Count unique companies
        unique_companies = set()
        for analysis in analyses:
            for mention in analysis.company_mentions:
                unique_companies.add(mention.company_name.lower())
        
        return ProcessingSummary(
            total_articles=total_articles,
            articles_with_mentions=articles_with_mentions,
            total_mentions=total_mentions,
            unique_companies=len(unique_companies),
        )


class ProcessingResult:
    """Result of the news contribution processing workflow."""
    
    def __init__(
        self,
        articles: List[Article],
        analyses: List[ArticleAnalysis],
        result_files: "ResultFiles",
        summary: "ProcessingSummary",
    ) -> None:
        """Initialize processing result.
        
        Args:
            articles: List of extracted articles
            analyses: List of analysis results
            result_files: Paths to exported files
            summary: Processing summary statistics
        """
        self.articles = articles
        self.analyses = analyses
        self.result_files = result_files
        self.summary = summary
    
    def __eq__(self, other: object) -> bool:
        """Compare ProcessingResult objects."""
        if not isinstance(other, ProcessingResult):
            return False
        return (self.articles == other.articles and
                self.analyses == other.analyses and
                self.result_files == other.result_files and
                self.summary == other.summary)
    
    @classmethod
    def empty(cls) -> "ProcessingResult":
        """Create an empty processing result."""
        return cls(
            articles=[],
            analyses=[],
            result_files=ResultFiles.empty(),
            summary=ProcessingSummary.empty(),
        )


class ResultFiles:
    """Paths to exported result files."""
    
    def __init__(self, main_results: Path, summary_stats: Path) -> None:
        """Initialize result files.
        
        Args:
            main_results: Path to main results CSV
            summary_stats: Path to summary statistics CSV
        """
        self.main_results = main_results
        self.summary_stats = summary_stats
    
    def __eq__(self, other: object) -> bool:
        """Compare ResultFiles objects."""
        if not isinstance(other, ResultFiles):
            return False
        return (self.main_results == other.main_results and 
                self.summary_stats == other.summary_stats)
    
    @classmethod
    def empty(cls) -> "ResultFiles":
        """Create empty result files."""
        return cls(
            main_results=Path(""),
            summary_stats=Path(""),
        )


class ProcessingSummary:
    """Summary statistics from processing."""
    
    def __init__(
        self,
        total_articles: int,
        articles_with_mentions: int,
        total_mentions: int,
        unique_companies: int,
    ) -> None:
        """Initialize processing summary.
        
        Args:
            total_articles: Total number of articles processed
            articles_with_mentions: Number of articles with company mentions
            total_mentions: Total number of company mentions found
            unique_companies: Number of unique companies mentioned
        """
        self.total_articles = total_articles
        self.articles_with_mentions = articles_with_mentions
        self.total_mentions = total_mentions
        self.unique_companies = unique_companies
    
    def __eq__(self, other: object) -> bool:
        """Compare ProcessingSummary objects."""
        if not isinstance(other, ProcessingSummary):
            return False
        return (self.total_articles == other.total_articles and
                self.articles_with_mentions == other.articles_with_mentions and
                self.total_mentions == other.total_mentions and
                self.unique_companies == other.unique_companies)
    
    @classmethod
    def empty(cls) -> "ProcessingSummary":
        """Create empty processing summary."""
        return cls(
            total_articles=0,
            articles_with_mentions=0,
            total_mentions=0,
            unique_companies=0,
        )
