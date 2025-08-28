"""Document processor for extracting articles from .docx files."""

import re
from pathlib import Path
from typing import Dict, List, Optional

from docx import Document
from docx.document import Document as DocumentType
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from pydantic import BaseModel

from .config import AppConfig
from .exceptions import DocumentProcessingError


class Article(BaseModel):
    """Represents a news article extracted from a document."""

    title: str
    source: str
    date: str
    content: str
    raw_text: str


class DocumentProcessor:
    """Processes .docx documents to extract news articles."""

    def __init__(self, data_directory: Path, config: Optional[AppConfig] = None) -> None:
        """Initialize the document processor.

        Args:
            data_directory: Path to directory containing .docx files
            config: Application configuration. If None, creates default config.
        """
        self.data_directory = Path(data_directory)
        self._config = config or AppConfig()

    def find_docx_files(self) -> List[Path]:
        """Find all .docx files in the data directory.

        Returns:
            List of paths to .docx files
        """
        return list(self.data_directory.glob("*.docx"))

    def extract_articles_from_file(self, file_path: Path) -> List[Article]:
        """Extract articles from a single .docx file.

        Args:
            file_path: Path to the .docx file

        Returns:
            List of extracted articles

        Raises:
            FileNotFoundError: If the file doesn't exist
            DocumentProcessingError: If the file cannot be processed
        """
        import logging
        logger = logging.getLogger("news_contribution_check.document_processor")
        
        logger.debug(f"Starting extraction from file: {file_path}", extra={
            'operation': 'file_extraction',
            'file_path': str(file_path)
        })
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}", extra={
                'operation': 'file_extraction',
                'file_path': str(file_path),
                'error_type': 'FileNotFoundError',
                'status': 'error'
            })
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            document = Document(file_path)
            articles = self._parse_document(document)
            
            logger.info(f"Successfully extracted {len(articles)} articles from {file_path}", extra={
                'operation': 'file_extraction',
                'file_path': str(file_path),
                'articles_extracted': len(articles),
                'status': 'success'
            })
            
            return articles
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}", extra={
                'operation': 'file_extraction',
                'file_path': str(file_path),
                'error_type': type(e).__name__,
                'error_message': str(e),
                'status': 'error'
            })
            raise DocumentProcessingError(
                f"Error processing file {file_path}: {e}",
                file_path=str(file_path),
                cause=e
            ) from e

    def _parse_document(self, document: DocumentType) -> List[Article]:
        """Parse document and extract individual articles.

        Args:
            document: The loaded Word document

        Returns:
            List of extracted articles
        """
        articles = []
        current_article_parts = []
        current_title = ""
        current_source = ""
        current_date = ""

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if not text:
                continue

            # Check if this is "End of Document" - indicates article boundary
            if text.lower() == "end of document":
                # Save previous article if we have content
                if current_article_parts and current_title:
                    article = self._create_article(
                        current_title,
                        current_source,
                        current_date,
                        current_article_parts,
                    )
                    if article:
                        articles.append(article)

                # Reset for new article
                current_article_parts = []
                current_title = ""
                current_source = ""
                current_date = ""
                continue

            # Try to extract metadata first
            source_match = self._extract_source(text)
            if source_match:
                current_source = source_match

            date_match = self._extract_date(text)
            if date_match:
                current_date = date_match

            # Check if this is a heading (potential article title)
            if self._is_heading(paragraph) and not current_title:
                current_title = text
            else:
                # Add all content to article parts (including metadata lines)
                current_article_parts.append(text)

        # Don't forget the last article
        if current_article_parts:
            article = self._create_article(
                current_title, current_source, current_date, current_article_parts
            )
            if article:
                articles.append(article)

        return articles

    def _is_heading(self, paragraph: Paragraph) -> bool:
        """Check if a paragraph is a heading.

        Args:
            paragraph: The paragraph to check

        Returns:
            True if the paragraph appears to be a heading
        """
        text = paragraph.text.strip()
        
        # Skip empty paragraphs
        if not text:
            return False
        
        # Skip obvious non-title content
        if any(skip_phrase in text.lower() for skip_phrase in [
            "byline:", "copyright", "end of document", "source:", "publication:",
            "dateline:", "length:", "word count:", "load-date:", "language:"
        ]):
            return False
        
        # Check for heading styles
        if paragraph.style and "heading" in paragraph.style.name.lower():
            return True

        # Check for bold formatting and appropriate length for titles
        if paragraph.runs:
            first_run = paragraph.runs[0]
            if (
                first_run.bold
                and 10 <= len(text) <= 200
                and not text.startswith(("By ", "From ", "Published ", "Updated "))
            ):
                return True

        # Check for title-like characteristics
        if (
            # Reasonable title length
            10 <= len(text) <= 150
            # Doesn't start with common article body patterns
            and not text.startswith(("The ", "A ", "An ", "In ", "On ", "At ", "By ", "From "))
            # Doesn't end with common non-title patterns
            and not text.endswith((":", ";", ","))
            # Contains capitalized words (title case)
            and sum(1 for word in text.split() if word and word[0].isupper()) >= 2
        ):
            return True

        return False

    def _extract_source(self, text: str) -> Optional[str]:
        """Extract publication source from text.

        Args:
            text: Text to search for source information

        Returns:
            Publication source if found, None otherwise
        """
        # Common patterns for source identification in news documents
        source_patterns = [
            # Copyright notices
            r"Copyright\s+\d{4}[^\n\r]*?([A-Z][a-zA-Z\s&.]+(?:News|Times|Post|Journal|Tribune|Herald|Globe|Daily|Weekly|Magazine|Review|Report|Wire|Press|Today|Business|Financial|Economic|Market|Trade|Industry|Technology|Tech|Online|Digital|Network|Media|Broadcasting|Television|TV|Radio|Reuters|Bloomberg|Associated Press|AP|CNN|BBC|NPR|Wall Street|Financial Times|FT|Chronicle|Gazette|Bulletin|Record|Examiner|Standard))",
            # Simple publication names at start of line
            r"^(The\s+[A-Z][a-zA-Z\s]+(?:Herald|Times|Post|Journal|Tribune|Globe|Daily|News|Weekly|Magazine|Review|Report|Wire|Press|Today|Business|Chronicle|Gazette|Bulletin|Record|Examiner|Standard))",
            # Publication names without "The"
            r"^([A-Z][a-zA-Z\s]+(?:Herald|Times|Post|Journal|Tribune|Globe|Daily|News|Weekly|Magazine|Review|Report|Wire|Press|Today|Business|Chronicle|Gazette|Bulletin|Record|Examiner|Standard))",
            # Explicit source labels
            r"Source:\s*([^\n\r]+)",
            r"Publication:\s*([^\n\r]+)",
            # Publication with dash separator
            r"^([A-Z][a-zA-Z\s&]+(?:Herald|Times|Post|Journal|Tribune|Globe|Daily|News)) -",
            # Common major news outlets
            r"\b(Reuters|Bloomberg|Associated Press|AP News|CNN|BBC|NPR|Wall Street Journal|Financial Times|USA Today|Washington Post|New York Times|Miami Herald|Sun Sentinel)\b",
        ]

        for pattern in source_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract and normalize publication date from text.

        Args:
            text: Text to search for date information

        Returns:
            Normalized date in YYYY-MM-DD format if found, None otherwise
        """
        # Date patterns to match various formats in news documents
        date_patterns = [
            # Standard formats
            r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            r"(\d{1,2}/\d{1,2}/\d{4})",  # MM/DD/YYYY or M/D/YYYY
            r"(\d{1,2}-\d{1,2}-\d{4})",  # MM-DD-YYYY or M-D-YYYY
            # Publication date formats
            r"Published:\s*(\d{1,2}/\d{1,2}/\d{4})",  # Published: MM/DD/YYYY
            r"Published:\s*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})",
            r"Load-Date:\s*(\d{1,2}/\d{1,2}/\d{4})",  # Load-Date: MM/DD/YYYY
            r"Load-Date:\s*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})",
            # Full month names
            r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})",  # Month DD, YYYY
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})",  # Mon DD, YYYY
            r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",  # DD Month YYYY
            # Year and month only
            r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",  # Month YYYY
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})",  # Mon YYYY
            r"(\d{4})",  # YYYY only
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._normalize_date(match.group(1))

        return None

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format.

        Args:
            date_str: Raw date string

        Returns:
            Normalized date in YYYY-MM-DD format
        """
        date_str = date_str.strip()

        # Month name mappings
        month_map = {
            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12",
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
        }

        # Already in YYYY-MM-DD format
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return date_str

        # MM/DD/YYYY or M/D/YYYY
        mm_dd_yyyy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", date_str)
        if mm_dd_yyyy:
            month, day, year = mm_dd_yyyy.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # MM-DD-YYYY or M-D-YYYY
        mm_dd_yyyy_dash = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", date_str)
        if mm_dd_yyyy_dash:
            month, day, year = mm_dd_yyyy_dash.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Month DD, YYYY or Mon DD, YYYY
        month_day_year = re.match(
            r"^(\w+)\s+(\d{1,2}),?\s+(\d{4})$", date_str, re.IGNORECASE
        )
        if month_day_year:
            month_name, day, year = month_day_year.groups()
            month_num = month_map.get(month_name.lower())
            if month_num:
                return f"{year}-{month_num}-{day.zfill(2)}"

        # DD Month YYYY
        day_month_year = re.match(
            r"^(\d{1,2})\s+(\w+)\s+(\d{4})$", date_str, re.IGNORECASE
        )
        if day_month_year:
            day, month_name, year = day_month_year.groups()
            month_num = month_map.get(month_name.lower())
            if month_num:
                return f"{year}-{month_num}-{day.zfill(2)}"

        # Month YYYY or Mon YYYY
        month_year = re.match(r"^(\w+)\s+(\d{4})$", date_str, re.IGNORECASE)
        if month_year:
            month_name, year = month_year.groups()
            month_num = month_map.get(month_name.lower())
            if month_num:
                return f"{year}-{month_num}-01"

        # YYYY only
        year_only = re.match(r"^(\d{4})$", date_str)
        if year_only:
            year = year_only.group(1)
            return f"{year}-01-01"

        # Fallback: return as-is or empty
        return date_str

    def _create_article(
        self, title: str, source: str, date: str, content_parts: List[str]
    ) -> Optional[Article]:
        """Create an Article object from extracted parts.

        Args:
            title: Article title
            source: Publication source
            date: Publication date
            content_parts: List of content paragraphs

        Returns:
            Article object if valid, None otherwise
        """
        if not title or not content_parts:
            return None

        content = "\n".join(content_parts)
        raw_text = f"Title: {title}\nSource: {source}\nDate: {date}\nContent: {content}"

        # Use fallback values if missing
        if not source:
            source = self._config.default_source
        if not date:
            date = self._config.default_date

        return Article(
            title=title.strip(),
            source=source.strip(),
            date=date.strip(),
            content=content.strip(),
            raw_text=raw_text.strip(),
        )

    def process_all_files(self) -> List[Article]:
        """Process all .docx files in the data directory.

        Returns:
            List of all extracted articles from all files

        Raises:
            DocumentProcessingError: If no .docx files are found or processing fails
        """
        import logging
        logger = logging.getLogger("news_contribution_check.document_processor")
        
        logger.info(f"Starting batch processing of files in directory: {self.data_directory}", extra={
            'operation': 'batch_processing',
            'data_directory': str(self.data_directory)
        })
        
        docx_files = self.find_docx_files()
        logger.info(f"Found {len(docx_files)} .docx files to process", extra={
            'operation': 'batch_processing',
            'files_found': len(docx_files)
        })

        if not docx_files:
            logger.error(f"No .docx files found in {self.data_directory}", extra={
                'operation': 'batch_processing',
                'data_directory': str(self.data_directory),
                'error_type': 'NoFilesFound',
                'status': 'error'
            })
            raise DocumentProcessingError(
                f"No .docx files found in {self.data_directory}",
                file_path=str(self.data_directory)
            )

        all_articles = []
        successful_files = 0
        failed_files = 0
        
        for file_path in docx_files:
            try:
                logger.debug(f"Processing file: {file_path}")
                articles = self.extract_articles_from_file(file_path)
                all_articles.extend(articles)
                successful_files += 1
                logger.debug(f"Successfully processed {file_path}: {len(articles)} articles")
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}", extra={
                    'operation': 'batch_processing',
                    'file_path': str(file_path),
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                failed_files += 1
                continue

        logger.info(f"Batch processing completed: {successful_files} successful, {failed_files} failed", extra={
            'operation': 'batch_processing',
            'total_files': len(docx_files),
            'successful_files': successful_files,
            'failed_files': failed_files,
            'total_articles': len(all_articles),
            'success_rate': successful_files / len(docx_files) if docx_files else 0
        })

        return all_articles