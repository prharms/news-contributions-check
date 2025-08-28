"""Logging configuration utilities for the news contribution check application."""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_dir: Optional[Path] = None,
    json_format: bool = False
) -> logging.Logger:
    """Setup application logging with enhanced configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_dir: Directory for log files (default: logs/)
        json_format: Whether to use JSON format for structured logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("news_contribution_check")
    
    # Clear existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        if json_format:
            console_formatter = _create_json_formatter()
        else:
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    if log_to_file:
        if log_dir is None:
            log_dir = Path("logs")
        
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "news_contribution_check.log")
        file_handler.setLevel(logging.DEBUG)  # File handler captures all levels
        
        if json_format:
            file_formatter = _create_json_formatter()
        else:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Log startup message
    logger.info("Logging system initialized", extra={
        'operation': 'logging_setup',
        'log_level': level,
        'handlers': [h.__class__.__name__ for h in logger.handlers],
        'json_format': json_format
    })
    
    return logger


def _create_json_formatter() -> logging.Formatter:
    """Create a JSON formatter for structured logging."""
    import json
    from datetime import datetime
    
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage()
            }
            
            # Add extra fields if present
            if hasattr(record, 'operation'):
                log_entry['operation'] = record.operation
            if hasattr(record, 'status'):
                log_entry['status'] = record.status
            if hasattr(record, 'error_type'):
                log_entry['error_type'] = record.error_type
            if hasattr(record, 'error_message'):
                log_entry['error_message'] = record.error_message
            
            return json.dumps(log_entry)
    
    return JsonFormatter()


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name (default: news_contribution_check)
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "news_contribution_check"
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """Set the logging level for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger("news_contribution_check")
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Update all handlers
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(log_level)
    
    logger.info(f"Log level changed to {level}", extra={
        'operation': 'log_level_change',
        'new_level': level
    })


def enable_debug_logging() -> None:
    """Enable debug logging for development."""
    set_log_level("DEBUG")


def enable_verbose_logging() -> None:
    """Enable verbose logging (INFO level with more details)."""
    set_log_level("INFO")


def enable_quiet_logging() -> None:
    """Enable quiet logging (WARNING and above only)."""
    set_log_level("WARNING")
