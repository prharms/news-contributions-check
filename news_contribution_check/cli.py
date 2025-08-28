"""Command-line interface for news contribution check."""

import argparse
from pathlib import Path

from .config import AppConfig
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
    args = parser.parse_args()

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