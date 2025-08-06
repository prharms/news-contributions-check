"""Command-line interface for news contribution check."""

import argparse

from .config import DEFAULT_DATA_DIRECTORY, DEFAULT_OUTPUT_DIRECTORY
from .main import main


def cli() -> None:
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(
        description="Extract company mentions from news articles using Claude AI"
    )
    parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIRECTORY,
        help=f"Directory containing .docx files (default: {DEFAULT_DATA_DIRECTORY})",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=f"Directory to save results (default: {DEFAULT_OUTPUT_DIRECTORY})",
    )
    args = parser.parse_args()

    main(
        data_directory=args.data_dir,
        output_directory=args.output_dir,
    )


if __name__ == "__main__":
    cli()