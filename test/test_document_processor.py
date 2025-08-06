"""Tests for document_processor module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from docx import Document
from docx.shared import Inches

from src.document_processor import Article, DocumentProcessor


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.processor = DocumentProcessor(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_find_docx_files_empty_directory(self) -> None:
        """Test finding files in empty directory."""
        files = self.processor.find_docx_files()
        assert files == []

    def test_find_docx_files_with_files(self) -> None:
        """Test finding files with .docx files present."""
        # Create test files
        docx_file = self.temp_dir / "test.docx"
        txt_file = self.temp_dir / "test.txt"
        
        docx_file.touch()
        txt_file.touch()
        
        files = self.processor.find_docx_files()
        assert len(files) == 1
        assert files[0] == docx_file

    def test_extract_articles_from_nonexistent_file(self) -> None:
        """Test extraction from non-existent file raises error."""
        non_existent = self.temp_dir / "nonexistent.docx"
        
        with pytest.raises(FileNotFoundError):
            self.processor.extract_articles_from_file(non_existent)

    def test_normalize_date_various_formats(self) -> None:
        """Test date normalization with various input formats."""
        test_cases = [
            ("2024-01-15", "2024-01-15"),
            ("1/15/2024", "2024-01-15"),
            ("01-15-2024", "2024-01-15"),
            ("January 15, 2024", "2024-01-15"),
            ("Jan 15, 2024", "2024-01-15"),
            ("15 January 2024", "2024-01-15"),
            ("January 2024", "2024-01-01"),
            ("Jan 2024", "2024-01-01"),
            ("2024", "2024-01-01"),
        ]
        
        for input_date, expected in test_cases:
            result = self.processor._normalize_date(input_date)
            assert result == expected, f"Failed for input: {input_date}"

    def test_extract_source_various_patterns(self) -> None:
        """Test source extraction with various patterns."""
        test_cases = [
            ("The Miami Herald - Company Reports", "The Miami Herald"),
            ("Source: Reuters News Service", "Reuters News Service"),
            ("Publication: Financial Times", "Financial Times"),
            ("Copyright 2024 The Miami Herald", "The Miami Herald"),
            ("Miami Herald", "Miami Herald"),
            ("The Wall Street Journal", "The Wall Street Journal"),
            ("Regular text without source", None),
        ]
        
        for text, expected in test_cases:
            result = self.processor._extract_source(text)
            assert result == expected, f"Failed for text: {text}"

    def test_extract_date_various_patterns(self) -> None:
        """Test date extraction with various patterns."""
        test_cases = [
            ("Published on 2024-01-15", "2024-01-15"),
            ("Date: January 15, 2024", "2024-01-15"),
            ("March 2024 report", "2024-03-01"),
            ("Published: 1/15/2024", "2024-01-15"),
            ("Load-Date: January 15, 2024", "2024-01-15"),
            ("Text without date", None),
        ]
        
        for text, expected in test_cases:
            result = self.processor._extract_date(text)
            assert result == expected, f"Failed for text: {text}"

    def test_create_article_valid_data(self) -> None:
        """Test article creation with valid data."""
        title = "Test Article"
        source = "Test Source"
        date = "2024-01-15"
        content_parts = ["Paragraph 1", "Paragraph 2"]
        
        article = self.processor._create_article(title, source, date, content_parts)
        
        assert article is not None
        assert article.title == title
        assert article.source == source
        assert article.date == date
        assert article.content == "Paragraph 1\nParagraph 2"

    def test_create_article_with_missing_data(self) -> None:
        """Test article creation with missing data uses defaults."""
        title = "Test Article"
        content_parts = ["Content"]
        
        article = self.processor._create_article("", "", "", content_parts)
        assert article is None
        
        article = self.processor._create_article(title, "", "", content_parts)
        assert article is not None
        assert article.source == "Unknown Source"
        assert article.date == "1900-01-01"

    def test_process_all_files_no_files(self) -> None:
        """Test processing with no .docx files raises error."""
        with pytest.raises(ValueError, match="No .docx files found"):
            self.processor.process_all_files()

    @patch('src.document_processor.Document')
    def test_extract_articles_from_file_success(self, mock_document: Mock) -> None:
        """Test successful article extraction from file."""
        # Create a test file
        test_file = self.temp_dir / "test.docx"
        test_file.touch()
        
        # Mock document structure
        mock_doc = Mock()
        mock_paragraph1 = Mock()
        mock_paragraph1.text = "Test Article Title"
        mock_paragraph1.style = Mock()
        mock_paragraph1.style.name = "Heading 1"
        mock_paragraph1.runs = [Mock(bold=True)]
        
        mock_paragraph2 = Mock()
        mock_paragraph2.text = "Source: Test News"
        mock_paragraph2.style = Mock()
        mock_paragraph2.style.name = "Normal"
        mock_paragraph2.runs = [Mock(bold=False)]
        
        mock_paragraph3 = Mock()
        mock_paragraph3.text = "Date: 2024-01-15"
        mock_paragraph3.style = Mock()
        mock_paragraph3.style.name = "Normal"
        mock_paragraph3.runs = [Mock(bold=False)]
        
        mock_paragraph4 = Mock()
        mock_paragraph4.text = "Article content here."
        mock_paragraph4.style = Mock()
        mock_paragraph4.style.name = "Normal"
        mock_paragraph4.runs = [Mock(bold=False)]
        
        mock_doc.paragraphs = [mock_paragraph1, mock_paragraph2, mock_paragraph3, mock_paragraph4]
        mock_document.return_value = mock_doc
        
        articles = self.processor.extract_articles_from_file(test_file)
        
        assert len(articles) == 1
        assert articles[0].title == "Test Article Title"


class TestArticle:
    """Test cases for Article model."""

    def test_article_creation(self) -> None:
        """Test article model creation."""
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        assert article.title == "Test Title"
        assert article.source == "Test Source"
        assert article.date == "2024-01-15"
        assert article.content == "Test content"
        assert article.raw_text == "Raw text"