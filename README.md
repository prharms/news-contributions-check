# News Contribution Check

A Python application that extracts company and organization mentions from news articles using Claude AI. The application processes Microsoft Word (.docx) files containing news articles and generates CSV reports of company mentions with detailed descriptions.

## Features

- Extract articles from .docx files with intelligent parsing
- Identify companies and organizations using Claude AI
- Generate structured CSV reports with citations
- Support for various date formats and publication sources
- Comprehensive test coverage (90%+)
- Summary statistics and publication breakdowns

## Requirements

- Python 3.8 or higher
- Anthropic API key for Claude AI access
- Microsoft Word documents (.docx) containing news articles

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd news_contribution_check
```

2. Install dependencies:
```bash
pip install -e .
```

   This will install the package and create the `analyze` console command.

3. Install development dependencies (optional):
```bash
pip install -e ".[dev]"
```

4. Set up your environment variables:
   - Copy the example file: `cp .env.example .env` (if available)
   - Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Basic Usage

1. Place your .docx files in the `data/` directory
2. Run the analysis:
```bash
analyze
```

### Advanced Usage

Run with custom parameters:
```bash
analyze --data-dir /path/to/docx/files --output-dir /path/to/output
```

You can also run as a Python module:
```bash
python -m news_contribution_check.main
```

### Command Line Options

- `--data-dir`: Directory containing .docx files (default: `data`)
- `--output-dir`: Directory to save results (default: `output`)

**Note**: The Anthropic API key must be set in your `.env` file for security reasons.

## Input Format

The application expects .docx files containing news articles with:

- **Article Separation**: Articles separated by heading styles or section breaks
- **Metadata**: Publication source and date information within articles
- **Content**: Full article text for analysis

### Example Article Structure
```
Article Title (Heading style)
Source: Wall Street Journal
Date: January 15, 2024
Article content mentioning Apple Inc. and Microsoft Corporation...
```

## Output Format

### File Naming Convention
Output files use timestamped filenames to prevent overwriting previous results:
- **Main results**: `company_mentions_YYYYMMDD_HHMMSS.csv`
- **Summary stats**: `summary_stats_YYYYMMDD_HHMMSS.csv`

Example: `company_mentions_20240115_143052.csv` (generated on Jan 15, 2024 at 2:30:52 PM)

### Main Results CSV
The primary output file contains:

| Column | Description |
|--------|-------------|
| Citations | Formatted as "Publication Name", "Exact Article Title" |
| Date | Publication date in YYYY-MM-DD format |
| Company/Organization Name | Exact name as mentioned in article |
| Description | Brief description (≤300 chars) of company's role |

### Summary Statistics CSV
Additional file with:
- Total articles processed
- Articles with company mentions
- Total company mentions found
- Unique companies mentioned
- Publication breakdown

## Date Handling

The application normalizes various date formats to YYYY-MM-DD:

- **Complete**: "January 15, 2024" → "2024-01-15"
- **Month/Year**: "May 2024" → "2024-05-01"
- **Year only**: "2022" → "2022-01-01"
- **Various formats**: MM/DD/YYYY, DD-MM-YYYY, etc.

Missing date components are filled with "01" as specified.

## Development

### Project Structure
```
news_contribution_check/
├── news_contribution_check/     # Main package
│   ├── __init__.py
│   ├── main.py                  # Core business logic
│   ├── cli.py                   # Command-line interface
│   ├── document_processor.py    # .docx file processing
│   ├── claude_analyzer.py       # Claude AI integration
│   ├── csv_exporter.py          # CSV output generation
│   └── config.py                # Configuration settings
├── test/                        # Test suite
├── data/                        # Input .docx files
├── output/                      # Generated reports
├── pyproject.toml               # Project configuration
├── .cursor-rules/               # Project rules and guidelines
└── README.md
```

### Running Tests

Run the full test suite:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=src --cov-report=html
```

Run specific test modules:
```bash
pytest test/test_document_processor.py
pytest test/test_claude_analyzer.py
```

### Code Quality

The project uses several tools for code quality:

- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting
- **mypy**: Static type checking
- **pytest**: Testing framework

Run all quality checks:
```bash
black src/ test/
flake8 src/ test/
isort src/ test/
mypy src/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:
```bash
pre-commit install
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Required. Your Anthropic Claude API key.

### Configuration

The application settings are centralized in `news_contribution_check/config.py`:

#### API Settings
- Model: `claude-sonnet-4-20250514` (Claude 4 Sonnet)
- Max tokens: 2000
- Temperature: 0.1 (for consistent results)

#### Processing Settings
- Max description length: 300 characters
- Default data directory: `data/`
- Default output directory: `output/`

To change the Claude model or other settings, edit the values in `news_contribution_check/config.py`.

## Error Handling

The application handles various error conditions:

- **Missing API key**: Clear error message with setup instructions
- **No .docx files**: Informative message about expected file location
- **Corrupted documents**: Individual file failures don't stop processing
- **API failures**: Graceful degradation with empty results for failed analyses
- **Invalid dates**: Fallback to default values as specified

## Performance Considerations

- **Large documents**: Articles are processed individually to manage memory
- **API rate limits**: Consider Anthropic's rate limits for bulk processing
- **Batch processing**: Multiple articles processed sequentially with progress indicators

## Limitations

- Only supports .docx format (not .doc or other formats)
- Requires Claude AI API access (paid service)
- Date extraction relies on common patterns (may miss unusual formats)
- Company identification depends on explicit mentions (not implied references)

## Contributing

1. Follow all rules in `.cursor-rules/RULES.md`
2. Maintain test coverage above 90%
3. Use conventional commit messages
4. Ensure all quality checks pass
5. Update documentation for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions:
1. Check the existing documentation
2. Review error messages and logs
3. Ensure API key is correctly configured  
4. Verify input file format matches expectations