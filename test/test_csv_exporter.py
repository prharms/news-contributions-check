"""Tests for csv_exporter module."""

import csv
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from news_contribution_check.claude_analyzer import ArticleAnalysis, CompanyMention
from news_contribution_check.csv_exporter import CSVExporter
from news_contribution_check.config import get_timestamped_filename
from news_contribution_check.exceptions import CSVExportError


class TestCSVExporter:
    """Test cases for CSVExporter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.exporter = CSVExporter(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_initialization(self) -> None:
        """Test CSV exporter initialization."""
        assert self.exporter.output_directory == self.temp_dir
        assert self.temp_dir.exists()

    def test_format_citation(self) -> None:
        """Test citation formatting."""
        citation = self.exporter._format_citation("Wall Street Journal", "Apple Reports Strong Q4")
        expected = '"Wall Street Journal", "Apple Reports Strong Q4"'
        assert citation == expected

    def test_export_results_with_mentions(self) -> None:
        """Test exporting results with company mentions."""
        analyses = [
            ArticleAnalysis(
                article_title="Tech News Today",
                publication_source="Tech Daily",
                publication_date="2024-01-15",
                company_mentions=[
                    CompanyMention(
                        company_name="Apple Inc.",
                        description="Technology company releasing new products"
                    ),
                    CompanyMention(
                        company_name="Microsoft Corporation",
                        description="Software giant expanding cloud services"
                    )
                ]
            ),
            ArticleAnalysis(
                article_title="Market Update",
                publication_source="Financial News",
                publication_date="2024-01-16",
                company_mentions=[
                    CompanyMention(
                        company_name="Tesla Inc.",
                        description="Electric vehicle manufacturer"
                    )
                ]
            )
        ]

        output_path = self.exporter.export_results(analyses, "test_output.csv")
        
        assert output_path.exists()
        
        # Read and verify CSV content
        with open(output_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            assert len(rows) == 3  # 2 mentions in first article + 1 in second
            
            # Check first article mentions
            assert rows[0]["Citations"] == '"Tech Daily", "Tech News Today"'
            assert rows[0]["Date"] == "2024-01-15"
            assert rows[0]["Company/Organization Name"] == "Apple Inc."
            assert "Technology company" in rows[0]["Description"]
            
            assert rows[1]["Citations"] == '"Tech Daily", "Tech News Today"'
            assert rows[1]["Date"] == "2024-01-15"
            assert rows[1]["Company/Organization Name"] == "Microsoft Corporation"
            assert "Software giant" in rows[1]["Description"]
            
            # Check second article mention
            assert rows[2]["Citations"] == '"Financial News", "Market Update"'
            assert rows[2]["Date"] == "2024-01-16"
            assert rows[2]["Company/Organization Name"] == "Tesla Inc."
            assert "Electric vehicle" in rows[2]["Description"]

    def test_export_results_no_mentions(self) -> None:
        """Test exporting results with no company mentions."""
        analyses = [
            ArticleAnalysis(
                article_title="Weather Update",
                publication_source="Weather Channel",
                publication_date="2024-01-15",
                company_mentions=[]
            )
        ]

        output_path = self.exporter.export_results(analyses, "test_no_mentions.csv")
        
        assert output_path.exists()
        
        # Read and verify CSV content
        with open(output_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            assert len(rows) == 1
            assert rows[0]["Citations"] == '"Weather Channel", "Weather Update"'
            assert rows[0]["Date"] == "2024-01-15"
            assert rows[0]["Company/Organization Name"] == ""
            assert "No companies or organizations mentioned" in rows[0]["Description"]

    def test_export_results_mixed_mentions(self) -> None:
        """Test exporting results with mixed mention patterns."""
        analyses = [
            ArticleAnalysis(
                article_title="Business News",
                publication_source="Business Today",
                publication_date="2024-01-15",
                company_mentions=[
                    CompanyMention(company_name="Google LLC", description="Search engine company")
                ]
            ),
            ArticleAnalysis(
                article_title="Sports News",
                publication_source="Sports Network",
                publication_date="2024-01-16",
                company_mentions=[]
            )
        ]

        output_path = self.exporter.export_results(analyses, "test_mixed.csv")
        
        assert output_path.exists()
        
        # Read and verify CSV content
        with open(output_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            assert len(rows) == 2
            
            # First article with mention
            assert rows[0]["Company/Organization Name"] == "Google LLC"
            assert "Search engine" in rows[0]["Description"]
            
            # Second article without mentions
            assert rows[1]["Company/Organization Name"] == ""
            assert "No companies or organizations mentioned" in rows[1]["Description"]

    def test_export_summary_stats(self) -> None:
        """Test exporting summary statistics."""
        analyses = [
            ArticleAnalysis(
                article_title="Article 1",
                publication_source="Publication A",
                publication_date="2024-01-15",
                company_mentions=[
                    CompanyMention(company_name="Apple Inc.", description="Tech company"),
                    CompanyMention(company_name="Microsoft Corporation", description="Software company")
                ]
            ),
            ArticleAnalysis(
                article_title="Article 2",
                publication_source="Publication A",
                publication_date="2024-01-16",
                company_mentions=[
                    CompanyMention(company_name="Apple Inc.", description="Another mention")
                ]
            ),
            ArticleAnalysis(
                article_title="Article 3",
                publication_source="Publication B",
                publication_date="2024-01-17",
                company_mentions=[]
            )
        ]

        output_path = self.exporter.export_summary_stats(analyses, "test_summary.csv")
        
        assert output_path.exists()
        
        # Read and verify CSV content
        with open(output_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            
            # Check summary statistics
            summary_section = rows[:5]  # First 5 rows are summary
            
            assert summary_section[0] == ["Summary Statistics"]
            assert summary_section[1] == ["Total Articles Processed", "3"]
            assert summary_section[2] == ["Articles with Company Mentions", "2"]
            assert summary_section[3] == ["Total Company Mentions", "3"]
            assert summary_section[4] == ["Unique Companies Mentioned", "2"]  # Apple and Microsoft
            
            # Check publication breakdown
            publication_section = rows[6:]  # After empty row
            assert publication_section[0] == ["Publication Breakdown"]
            assert publication_section[1] == ["Publication", "Articles", "Total Mentions"]
            
            # Should have data for both publications
            pub_data = publication_section[2:]
            assert len(pub_data) == 2
            
            # Check data (sorted alphabetically)
            pub_a_row = next(row for row in pub_data if row[0] == "Publication A")
            pub_b_row = next(row for row in pub_data if row[0] == "Publication B")
            
            assert pub_a_row == ["Publication A", "2", "3"]  # 2 articles, 3 mentions
            assert pub_b_row == ["Publication B", "1", "0"]  # 1 article, 0 mentions

    def test_export_results_custom_filename(self) -> None:
        """Test exporting with custom filename."""
        analyses = [
            ArticleAnalysis(
                article_title="Test",
                publication_source="Test Source",
                publication_date="2024-01-15",
                company_mentions=[]
            )
        ]

        output_path = self.exporter.export_results(analyses, "custom_name.csv")
        
        assert output_path.name == "custom_name.csv"
        assert output_path.exists()

    def test_export_results_failure_handling(self) -> None:
        """Test export failure handling."""
        # Create exporter with valid directory but cause export failure
        exporter = CSVExporter(self.temp_dir)
        
        analyses = [
            ArticleAnalysis(
                article_title="Test",
                publication_source="Test Source",
                publication_date="2024-01-15",
                company_mentions=[]
            )
        ]

        # Mock open() to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with pytest.raises(CSVExportError) as exc_info:
                exporter.export_results(analyses)
            
            error = exc_info.value
            assert "Failed to export CSV" in str(error)
            assert "Access denied" in str(error)
            assert error.file_path is not None
            assert error.cause is not None

    def test_timestamped_filename_generation(self) -> None:
        """Test that timestamped filenames are generated correctly."""
        import re
        
        # Test the get_timestamped_filename function
        filename = get_timestamped_filename("company_mentions")
        
        # Should match pattern: company_mentions_YYYYMMDD_HHMMSS.csv
        pattern = r"company_mentions_\d{8}_\d{6}\.csv"
        assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"
        
        # Test with custom extension
        filename_json = get_timestamped_filename("summary", "json")
        pattern_json = r"summary_\d{8}_\d{6}\.json"
        assert re.match(pattern_json, filename_json), f"Filename {filename_json} doesn't match expected pattern"

    def test_export_results_with_timestamped_filename(self) -> None:
        """Test exporting results with automatic timestamped filename."""
        analyses = [
            ArticleAnalysis(
                article_title="Test Article",
                publication_source="Test Source",
                publication_date="2024-01-15",
                company_mentions=[
                    CompanyMention(
                        company_name="Test Company",
                        description="Test description"
                    )
                ]
            )
        ]
        
        # Export without specifying filename (should use timestamped)
        output_path = self.exporter.export_results(analyses)
        
        # Verify file was created and has timestamped name
        assert output_path.exists()
        assert "company_mentions_" in output_path.name
        assert output_path.suffix == ".csv"
        
        # Verify content is correct
        with open(output_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["Company/Organization Name"] == "Test Company"

    def test_export_summary_stats_with_timestamped_filename(self) -> None:
        """Test exporting summary stats with automatic timestamped filename."""
        analyses = [
            ArticleAnalysis(
                article_title="Test Article",
                publication_source="Test Source", 
                publication_date="2024-01-15",
                company_mentions=[
                    CompanyMention(
                        company_name="Test Company",
                        description="Test description"
                    )
                ]
            )
        ]
        
        # Export without specifying filename (should use timestamped)
        output_path = self.exporter.export_summary_stats(analyses)
        
        # Verify file was created and has timestamped name
        assert output_path.exists()
        assert "summary_stats_" in output_path.name
        assert output_path.suffix == ".csv"