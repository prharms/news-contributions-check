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
        "file",
        help="Specific .docx file to process (must be in the data directory)",
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
    parser.add_argument(
        "--compare-to-cf",
        metavar="CF_CSV_FILENAME",
        help="Compare results to a campaign finance CSV in the data directory",
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
    
    # Validate and construct the full file path
    data_dir = Path(config.data_directory)
    provided_arg = str(args.file)
    file_path = Path(provided_arg)
    
    # Avoid double-prefixing: only join when the provided relative path does not already start with data dir
    norm_data = str(data_dir).replace("\\", "/").rstrip("/")
    norm_provided = provided_arg.replace("\\", "/")
    should_join = (not file_path.is_absolute()) and not (
        norm_provided.startswith(norm_data + "/") or norm_provided == norm_data
    )
    if should_join:
        file_path = data_dir / provided_arg
    
    # Validate the file exists and is in the data directory
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return 1
    
    # Ensure final path is within data directory
    norm_final = str(file_path).replace("\\", "/")
    if not norm_final.startswith(norm_data + "/") and norm_final != norm_data:
        print(f"[ERROR] File must be within the data directory: {data_dir}")
        return 1
    
    if file_path.suffix.lower() != '.docx':
        print(f"[ERROR] File must be a .docx file: {file_path}")
        return 1
    
    # Use provided arguments or config defaults
    output_dir = args.output_dir or config.output_directory

    # Build string for main() preserving leading '/' if present in config path
    file_path_str = str(file_path)
    if isinstance(config.data_directory, str) and config.data_directory.startswith('/'):
        if not provided_arg.startswith(('/', '\\')):
            file_path_str = config.data_directory.rstrip('/\\') + "\\" + provided_arg.lstrip('/\\')

    result = main(
        file_path=str(file_path_str),
        output_directory=output_dir,
    )

    # Optional CF comparison
    if args.compare_to_cf:
        from .container import Container
        container = Container()
        matcher = container.get_cf_matcher()
        try:
            report_path = matcher.compare(
                company_csv=result.result_files.main_results,
                cf_csv_filename=args.compare_to_cf,
            )
            print(f"Comparison report written to: {report_path}")
        except Exception as e:
            print(f"[ERROR] CF comparison failed: {e}")


if __name__ == "__main__":
    cli()