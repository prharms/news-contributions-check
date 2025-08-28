"""Command-line interface for news contribution check."""

import argparse
from pathlib import Path

from .config import AppConfig
from .logging_config import setup_logging, enable_debug_logging, enable_quiet_logging
from .main import main


def cli() -> None:
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(
        description="Extract company mentions from news articles using Claude AI"
    )
    parser.add_argument(
        "--data-dir",
        help="Directory containing .docx files (default: from config)",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to save results (default: from config)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Enable quiet logging (warnings and errors only)",
    )
    parser.add_argument(
        "--no-file-logging",
        action="store_true",
        help="Disable file logging",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Use JSON format for structured logging",
    )
    args = parser.parse_args()

    # Setup logging based on arguments
    if args.debug:
        setup_logging(level="DEBUG", log_to_file=not args.no_file_logging, json_format=args.json_logs)
        enable_debug_logging()
    elif args.verbose:
        setup_logging(level="INFO", log_to_file=not args.no_file_logging, json_format=args.json_logs)
    elif args.quiet:
        setup_logging(level="WARNING", log_to_file=not args.no_file_logging, json_format=args.json_logs)
        enable_quiet_logging()
    else:
        setup_logging(level="INFO", log_to_file=not args.no_file_logging, json_format=args.json_logs)

    # Load config to get defaults
    config = AppConfig()
    
    # Use provided arguments or config defaults
    data_dir = args.data_dir or config.data_directory
    output_dir = args.output_dir or config.output_directory

    main(
        data_directory=data_dir,
        output_directory=output_dir,
    )


if __name__ == "__main__":
    cli()