"""Interfaces and protocols for the news contribution check application."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Protocol

from .document_processor import Article
from .claude_analyzer import ArticleAnalysis


class DocumentProcessorProtocol(Protocol):
    """Protocol for document processing functionality."""
    
    def find_docx_files(self) -> List[Path]:
        """Find all .docx files in the data directory."""
        ...
    
    def extract_articles_from_file(self, file_path: Path) -> List[Article]:
        """Extract articles from a single .docx file."""
        ...
    
    def process_all_files(self) -> List[Article]:
        """Process all .docx files in the data directory."""
        ...


class ClaudeAnalyzerProtocol(Protocol):
    """Protocol for Claude AI analysis functionality."""
    
    def analyze_article(self, article: Article) -> ArticleAnalysis:
        """Analyze a single article to extract company mentions."""
        ...
    
    def analyze_articles(self, articles: List[Article]) -> List[ArticleAnalysis]:
        """Analyze multiple articles to extract company mentions."""
        ...


class CSVExporterProtocol(Protocol):
    """Protocol for CSV export functionality."""
    
    def export_results(self, analyses: List[ArticleAnalysis], filename: str = None) -> Path:
        """Export analysis results to CSV file."""
        ...
    
    def export_summary_stats(self, analyses: List[ArticleAnalysis], filename: str = None) -> Path:
        """Export summary statistics to CSV file."""
        ...


class ConfigurationProvider(ABC):
    """Abstract base class for configuration providers."""
    
    @abstractmethod
    def get_api_key(self) -> str:
        """Get API key for external services."""
        pass
    
    @abstractmethod
    def get_data_directory(self) -> str:
        """Get data directory path."""
        pass
    
    @abstractmethod
    def get_output_directory(self) -> str:
        """Get output directory path."""
        pass
    
    @abstractmethod
    def get_max_description_length(self) -> int:
        """Get maximum description length."""
        pass


class LoggerProtocol(Protocol):
    """Protocol for logging functionality."""
    
    def info(self, message: str) -> None:
        """Log info message."""
        ...
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        ...
    
    def error(self, message: str) -> None:
        """Log error message."""
        ...
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        ...


class FileSystemProtocol(Protocol):
    """Protocol for file system operations."""
    
    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        ...
    
    def mkdir(self, path: Path, parents: bool = False, exist_ok: bool = False) -> None:
        """Create directory."""
        ...
    
    def glob(self, path: Path, pattern: str) -> List[Path]:
        """Find files matching pattern."""
        ...
