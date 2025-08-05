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

from .config import DEFAULT_DATE, DEFAULT_SOURCE


class Article(BaseModel):
    """Represents a news article extracted from a document."""

    title: str
    source: str
    date: str
    content: str
    raw_text: str


class DocumentProcessor:
    """Processes .docx documents to extract news articles."""

    def __init__(self, data_directory: Path) -> None:
        """Initialize the document processor.

        Args:
            data_directory: Path to directory containing .docx files
        """
        self.data_directory = Path(data_directory)

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
            ValueError: If the file cannot be processed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            document = Document(file_path)
            return self._parse_document(document)
        except Exception as e:
            raise ValueError(f"Error processing file {file_path}: {e}") from e

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

            # Check if this is a heading (potential article separator)
            if self._is_heading(paragraph):
                # Save previous article if we have content
                if current_article_parts:
                    article = self._create_article(
                        current_title,
                        current_source,
                        current_date,
                        current_article_parts,
                    )
                    if article:
                        articles.append(article)

                # Start new article
                current_article_parts = []
                current_title = text
                current_source = ""
                current_date = ""
            else:
                # Try to extract metadata from the paragraph
                source_match = self._extract_source(text)
                if source_match:
                    current_source = source_match

                date_match = self._extract_date(text)
                if date_match:
                    current_date = date_match

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
        # Check for heading styles
        if paragraph.style and "heading" in paragraph.style.name.lower():
            return True

        # Check for bold formatting and short length
        if paragraph.runs:
            first_run = paragraph.runs[0]
            if (
                first_run.bold
                and len(paragraph.text.strip()) < 200
                and len(paragraph.text.strip()) > 10
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
        # Common patterns for source identification
        source_patterns = [
            r"^([A-Z][a-zA-Z\s&]+(?:News|Times|Post|Journal|Tribune|Herald|Globe|Daily|Weekly|Magazine|Review|Report|Wire|Press|Today|Business|Financial|Economic|Market|Trade|Industry|Technology|Tech|Online|Digital|Network|Media|Broadcasting|Television|TV|Radio|Reuters|Bloomberg|Associated Press|AP|CNN|BBC|NPR|Wall Street|Financial Times|FT|USA Today|Washington Post|New York Times|NYT|Guardian|Independent|Telegraph|Observer|Mirror|Express|Mail|Sun|Star|Chronicle|Gazette|Bulletin|Record|Leader|Sentinel|Register|Examiner|Standard|Voice|View|Opinion|Commentary|Analysis|Insight|Focus|Special|Update|Alert|Briefing|Summary|Overview|Spotlight|Feature|Profile|Interview|Investigation|Exclusive|Breaking|Latest|Current|Live|Now|Today|This Week|This Month|This Year)):",
            r"Source:\s*([^\n\r]+)",
            r"Publication:\s*([^\n\r]+)",
            r"^([A-Z][a-zA-Z\s&]+ - )",
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
        # Date patterns to match various formats
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            r"(\d{1,2}/\d{1,2}/\d{4})",  # MM/DD/YYYY or M/D/YYYY
            r"(\d{1,2}-\d{1,2}-\d{4})",  # MM-DD-YYYY or M-D-YYYY
            r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})",  # Month DD, YYYY
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})",  # Mon DD, YYYY
            r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",  # DD Month YYYY
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
            source = DEFAULT_SOURCE
        if not date:
            date = DEFAULT_DATE

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
            ValueError: If no .docx files are found or processing fails
        """
        docx_files = self.find_docx_files()

        if not docx_files:
            raise ValueError(f"No .docx files found in {self.data_directory}")

        all_articles = []
        for file_path in docx_files:
            try:
                articles = self.extract_articles_from_file(file_path)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}")
                continue

        return all_articles