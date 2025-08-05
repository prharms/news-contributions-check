"""CSV export functionality for analysis results."""

import csv
from pathlib import Path
from typing import List

from .claude_analyzer import ArticleAnalysis
from .config import DEFAULT_CSV_FILENAME, DEFAULT_SUMMARY_FILENAME


class CSVExporter:
    """Exports analysis results to CSV format."""

    def __init__(self, output_directory: Path = Path("output")) -> None:
        """Initialize the CSV exporter.

        Args:
            output_directory: Directory to save CSV files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)

    def export_results(
        self, analyses: List[ArticleAnalysis], filename: str = DEFAULT_CSV_FILENAME
    ) -> Path:
        """Export analysis results to CSV file.

        Args:
            analyses: List of article analyses to export
            filename: Name of the output CSV file

        Returns:
            Path to the created CSV file

        Raises:
            ValueError: If export fails
        """
        output_path = self.output_directory / filename

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Citations", "Date", "Company/Organization Name", "Description"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for analysis in analyses:
                    citation = self._format_citation(
                        analysis.publication_source, analysis.article_title
                    )

                    if not analysis.company_mentions:
                        # Write a row even if no companies were found
                        writer.writerow(
                            {
                                "Citations": citation,
                                "Date": analysis.publication_date,
                                "Company/Organization Name": "",
                                "Description": "No companies or organizations mentioned",
                            }
                        )
                    else:
                        for mention in analysis.company_mentions:
                            writer.writerow(
                                {
                                    "Citations": citation,
                                    "Date": analysis.publication_date,
                                    "Company/Organization Name": mention.company_name,
                                    "Description": mention.description,
                                }
                            )

            print(f"Results exported to: {output_path}")
            return output_path

        except Exception as e:
            raise ValueError(f"Failed to export CSV: {e}") from e

    def _format_citation(self, publication_source: str, article_title: str) -> str:
        """Format citation according to specification.

        Args:
            publication_source: Name of the publication
            article_title: Title of the article

        Returns:
            Formatted citation string
        """
        # Format: "Publication Name", "Exact Article Title"
        return f'"{publication_source}", "{article_title}"'

    def export_summary_stats(
        self, analyses: List[ArticleAnalysis], filename: str = DEFAULT_SUMMARY_FILENAME
    ) -> Path:
        """Export summary statistics to CSV file.

        Args:
            analyses: List of article analyses
            filename: Name of the summary CSV file

        Returns:
            Path to the created summary CSV file
        """
        output_path = self.output_directory / filename

        # Calculate statistics
        total_articles = len(analyses)
        total_mentions = sum(len(analysis.company_mentions) for analysis in analyses)
        articles_with_mentions = sum(
            1 for analysis in analyses if analysis.company_mentions
        )

        # Count unique companies
        unique_companies = set()
        for analysis in analyses:
            for mention in analysis.company_mentions:
                unique_companies.add(mention.company_name.lower())

        # Count mentions by publication
        publication_counts = {}
        for analysis in analyses:
            source = analysis.publication_source
            if source not in publication_counts:
                publication_counts[source] = {"articles": 0, "mentions": 0}
            publication_counts[source]["articles"] += 1
            publication_counts[source]["mentions"] += len(analysis.company_mentions)

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write summary statistics
                writer.writerow(["Summary Statistics"])
                writer.writerow(["Total Articles Processed", total_articles])
                writer.writerow(["Articles with Company Mentions", articles_with_mentions])
                writer.writerow(["Total Company Mentions", total_mentions])
                writer.writerow(["Unique Companies Mentioned", len(unique_companies)])
                writer.writerow([])

                # Write publication breakdown
                writer.writerow(["Publication Breakdown"])
                writer.writerow(["Publication", "Articles", "Total Mentions"])
                for publication, counts in sorted(publication_counts.items()):
                    writer.writerow([publication, counts["articles"], counts["mentions"]])

            print(f"Summary statistics exported to: {output_path}")
            return output_path

        except Exception as e:
            raise ValueError(f"Failed to export summary statistics: {e}") from e