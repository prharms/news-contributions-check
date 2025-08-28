"""Composition root and dependency injection container for the application."""

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .claude_analyzer import ClaudeAnalyzer
from .config import AppConfig
from .csv_exporter import CSVExporter
from .document_processor import DocumentProcessor


class Container:
    """Application composition root that manages dependencies and their lifecycle."""
    
    def __init__(self, config: Optional[AppConfig] = None) -> None:
        """Initialize the container with configuration.
        
        Args:
            config: Application configuration. If None, loads from environment.
        """
        self._config = config or self._load_config()
        self._logger = self._setup_logging()
        self._claude_analyzer: Optional[ClaudeAnalyzer] = None
        self._document_processor: Optional[DocumentProcessor] = None
        self._csv_exporter: Optional[CSVExporter] = None
    
    def _load_config(self) -> AppConfig:
        """Load configuration from environment variables."""
        load_dotenv()
        return AppConfig()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup application logging."""
        logger = logging.getLogger("news_contribution_check")
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @property
    def config(self) -> AppConfig:
        """Get application configuration."""
        return self._config
    
    @property
    def logger(self) -> logging.Logger:
        """Get application logger."""
        return self._logger
    
    def get_claude_analyzer(self) -> ClaudeAnalyzer:
        """Get or create Claude analyzer instance."""
        if self._claude_analyzer is None:
            api_key = self._config.get_api_key()
            self._claude_analyzer = ClaudeAnalyzer(api_key=api_key)
        return self._claude_analyzer
    
    def get_document_processor(self, data_directory: Optional[Path] = None) -> DocumentProcessor:
        """Get or create document processor instance.
        
        Args:
            data_directory: Directory containing .docx files. If None, uses config default.
        """
        if self._document_processor is None:
            if data_directory is None:
                data_directory = Path(self._config.data_directory)
            self._document_processor = DocumentProcessor(data_directory)
        return self._document_processor
    
    def get_csv_exporter(self, output_directory: Optional[Path] = None) -> CSVExporter:
        """Get or create CSV exporter instance.
        
        Args:
            output_directory: Directory to save CSV files. If None, uses config default.
        """
        if self._csv_exporter is None:
            if output_directory is None:
                output_directory = Path(self._config.output_directory)
            self._csv_exporter = CSVExporter(output_directory)
        return self._csv_exporter
    
    def reset(self) -> None:
        """Reset all cached instances (useful for testing)."""
        self._claude_analyzer = None
        self._document_processor = None
        self._csv_exporter = None
