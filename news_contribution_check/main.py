"""Main script for news contribution check analysis."""

import sys
from pathlib import Path
from typing import Optional

from .container import Container
from .exceptions import NewsContributionCheckError
from .orchestrator import NewsContributionOrchestrator


def main(
    data_directory: str = None,
    output_directory: str = None,
) -> None:
    """Main function to process news articles and extract company mentions.

    Args:
        data_directory: Directory containing .docx files. If None, uses config default.
        output_directory: Directory to save results. If None, uses config default.

    Raises:
        SystemExit: If processing fails
    """
    try:
        print("News Contribution Check - Company Mention Extraction")
        print("=" * 55)

        # Initialize container and dependencies
        container = Container()
        
        # Convert string paths to Path objects if provided
        data_path = Path(data_directory) if data_directory else None
        output_path = Path(output_directory) if output_directory else None
        
        # Create orchestrator with dependencies from container
        orchestrator = NewsContributionOrchestrator(
            document_processor=container.get_document_processor(data_path),
            claude_analyzer=container.get_claude_analyzer(),
            csv_exporter=container.get_csv_exporter(output_path),
            logger=container.logger,
            config=container.config,
        )

        # Process news articles
        result = orchestrator.process_news_articles(data_path, output_path)

        # Print results
        _print_processing_results(result)

    except NewsContributionCheckError as e:
        print(f"Error during processing: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def _print_processing_results(result) -> None:
    """Print processing results to console.
    
    Args:
        result: ProcessingResult from orchestrator
    """
    print("\nProcessing Complete!")
    print("=" * 20)
    print(f"Total articles processed: {result.summary.total_articles}")
    print(f"Articles with company mentions: {result.summary.articles_with_mentions}")
    print(f"Total company mentions found: {result.summary.total_mentions}")
    print(f"Unique companies mentioned: {result.summary.unique_companies}")
    print(f"Results saved to: {result.result_files.main_results}")
    print(f"Summary statistics: {result.result_files.summary_stats}")


if __name__ == "__main__":
    # For direct execution, import and use CLI
    from .cli import cli
    cli()