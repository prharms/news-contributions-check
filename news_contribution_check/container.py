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
from .logging_config import setup_logging


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
        """Setup application logging with enhanced configuration."""
        return setup_logging(
            level="INFO",
            log_to_file=True,
            log_to_console=True
        )
    
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
            try:
                self._logger.debug("Creating new ClaudeAnalyzer instance")
                api_key = self._config.get_api_key()
                self._claude_analyzer = ClaudeAnalyzer(api_key=api_key, config=self._config)
                self._logger.info("ClaudeAnalyzer instance created successfully", extra={
                    'operation': 'claude_analyzer_creation',
                    'status': 'success'
                })
            except Exception as e:
                self._logger.error("Failed to create ClaudeAnalyzer instance", extra={
                    'operation': 'claude_analyzer_creation',
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                raise
        return self._claude_analyzer
    
    def get_document_processor(self, data_directory: Optional[Path] = None) -> DocumentProcessor:
        """Get or create document processor instance.
        
        Args:
            data_directory: Directory containing .docx files. If None, uses config default.
        """
        if self._document_processor is None:
            try:
                if data_directory is None:
                    data_directory = Path(self._config.data_directory)
                
                self._logger.debug(f"Creating new DocumentProcessor instance for directory: {data_directory}")
                self._document_processor = DocumentProcessor(data_directory, config=self._config)
                self._logger.info("DocumentProcessor instance created successfully", extra={
                    'operation': 'document_processor_creation',
                    'data_directory': str(data_directory),
                    'status': 'success'
                })
            except Exception as e:
                self._logger.error("Failed to create DocumentProcessor instance", extra={
                    'operation': 'document_processor_creation',
                    'data_directory': str(data_directory) if data_directory else 'default',
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                raise
        return self._document_processor
    
    def get_csv_exporter(self, output_directory: Optional[Path] = None) -> CSVExporter:
        """Get or create CSV exporter instance.
        
        Args:
            output_directory: Directory to save CSV files. If None, uses config default.
        """
        if self._csv_exporter is None:
            try:
                if output_directory is None:
                    output_directory = Path(self._config.output_directory)
                
                self._logger.debug(f"Creating new CSVExporter instance for directory: {output_directory}")
                self._csv_exporter = CSVExporter(output_directory)
                self._logger.info("CSVExporter instance created successfully", extra={
                    'operation': 'csv_exporter_creation',
                    'output_directory': str(output_directory),
                    'status': 'success'
                })
            except Exception as e:
                self._logger.error("Failed to create CSVExporter instance", extra={
                    'operation': 'csv_exporter_creation',
                    'output_directory': str(output_directory) if output_directory else 'default',
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                raise
        return self._csv_exporter
    
    def reset(self) -> None:
        """Reset all cached instances (useful for testing)."""
        self._claude_analyzer = None
        self._document_processor = None
        self._csv_exporter = None
