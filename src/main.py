"""Main script for news contribution check analysis."""

import sys
from pathlib import Path
from typing import Optional

from .claude_analyzer import ClaudeAnalyzer
from .config import DEFAULT_DATA_DIRECTORY, DEFAULT_OUTPUT_DIRECTORY
from .csv_exporter import CSVExporter
from .document_processor import DocumentProcessor


def main(
    data_directory: str = DEFAULT_DATA_DIRECTORY,
    output_directory: str = DEFAULT_OUTPUT_DIRECTORY,
    api_key: Optional[str] = None,
) -> None:
    """Main function to process news articles and extract company mentions.

    Args:
        data_directory: Directory containing .docx files
        output_directory: Directory to save results
        api_key: Anthropic API key (optional, can use environment variable)

    Raises:
        SystemExit: If processing fails
    """
    try:
        print("News Contribution Check - Company Mention Extraction")
        print("=" * 55)

        # Initialize components
        print(f"Initializing document processor for directory: {data_directory}")
        
        # Ensure data directory exists
        data_path = Path(data_directory)
        if not data_path.exists():
            print(f"Creating data directory: {data_path}")
            data_path.mkdir(parents=True, exist_ok=True)
        
        doc_processor = DocumentProcessor(data_path)

        print("Initializing Claude analyzer...")
        claude_analyzer = ClaudeAnalyzer(api_key)

        print(f"Initializing CSV exporter for directory: {output_directory}")
        
        # Ensure output directory exists
        output_path = Path(output_directory)
        if not output_path.exists():
            print(f"Creating output directory: {output_path}")
            output_path.mkdir(parents=True, exist_ok=True)
            
        csv_exporter = CSVExporter(output_path)

        # Process documents
        print("\nStep 1: Extracting articles from .docx files...")
        articles = doc_processor.process_all_files()
        print(f"Extracted {len(articles)} articles from {len(doc_processor.find_docx_files())} files")

        if not articles:
            print("No articles found. Exiting.")
            return

        # Analyze articles with Claude
        print("\nStep 2: Analyzing articles with Claude AI...")
        analyses = claude_analyzer.analyze_articles(articles)
        print(f"Completed analysis of {len(analyses)} articles")

        # Export results
        print("\nStep 3: Exporting results to CSV...")
        main_csv_path = csv_exporter.export_results(analyses)
        summary_csv_path = csv_exporter.export_summary_stats(analyses)

        # Print summary
        total_mentions = sum(len(analysis.company_mentions) for analysis in analyses)
        articles_with_mentions = sum(
            1 for analysis in analyses if analysis.company_mentions
        )

        print("\nProcessing Complete!")
        print("=" * 20)
        print(f"Total articles processed: {len(articles)}")
        print(f"Articles with company mentions: {articles_with_mentions}")
        print(f"Total company mentions found: {total_mentions}")
        print(f"Results saved to: {main_csv_path}")
        print(f"Summary statistics: {summary_csv_path}")

    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

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
    parser.add_argument(
        "--api-key", help="Anthropic API key (optional, can use ANTHROPIC_API_KEY env var)"
    )

    args = parser.parse_args()

    main(
        data_directory=args.data_dir,
        output_directory=args.output_dir,
        api_key=args.api_key,
    )