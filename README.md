# News Contribution Check

A Python application that extracts company and organization mentions from news articles using Claude AI. The application processes Microsoft Word (.docx) files containing news articles and generates CSV reports of company mentions with detailed descriptions.

## Features

- Extract articles from .docx files with intelligent parsing
- Identify companies and organizations using Claude AI
- Generate structured CSV reports with citations
- Support for various date formats and publication sources
- **Object-Oriented Architecture**: Built with SOLID principles and dependency injection
- **Comprehensive Test Coverage**: 91.6% overall coverage with 80%+ per module
- Summary statistics and publication breakdowns
- **Forensic-grade analysis**: Excludes government entities (cities, counties, states, federal agencies) and media organizations

## Architecture

### SOLID Principles Implementation

The application follows Object-Oriented Programming and SOLID principles:

- **Single Responsibility Principle (SRP)**: Each class has one reason to change
- **Open/Closed Principle (OCP)**: Open for extension, closed for modification
- **Liskov Substitution Principle (LSP)**: Components are swappable without breaking callers
- **Interface Segregation Principle (ISP)**: Depend on focused interfaces
- **Dependency Inversion Principle (DIP)**: High-level modules own abstractions

### Core Components

- **Container**: Composition root managing dependency lifecycle
- **NewsContributionOrchestrator**: Central service coordinating the workflow
- **DocumentProcessor**: Handles .docx file processing and article extraction
- **ClaudeAnalyzer**: Manages AI analysis and Claude API integration
- **CSVExporter**: Handles CSV output generation and formatting
- **Configuration**: Class-based configuration with validation

### Dependency Injection

All components receive dependencies via constructor injection, enabling:
- Easy testing with mocks and fakes
- Loose coupling between components
- Clear separation of concerns
- Flexible configuration and customization

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
   - Copy the example file: `cp env.example .env` (if available)
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
- `--verbose, -v`: Enable verbose logging

**Note**: The Anthropic API key must be set in your environment variables for security reasons.

## Analysis Methodology

### Forensic Document Analysis
The application uses Claude AI configured as a forensic document analyst to ensure results meet standards for documentary evidence in litigation. The analysis follows strict guidelines:

- **Zero creativity**: Only factual extraction of explicitly mentioned entities
- **Mandatory exclusions**: Government entities and media organizations are systematically excluded
- **Structured validation**: Each potential company/organization is verified against exclusion criteria

### Exclusion Criteria
The system automatically excludes the following entities from company/organization identification:

- **Government Entities**: Cities, counties, states, federal agencies, and government departments
- **Media Organizations**: Newspapers, news outlets, and other media companies (unless they are the subject of the story)
- **Generic References**: Terms like "the company" or "the organization" without proper names

### Validation Checklist
Before identifying any entity as a company/organization, the system verifies it is:
- NOT a city
- NOT a county  
- NOT a state
- NOT the federal government
- NOT the name of a newspaper
- NOT the name of other news media

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
│   ├── main.py                  # Application entry point
│   ├── cli.py                   # Command-line interface
│   ├── orchestrator.py          # Main workflow coordination
│   ├── container.py             # Dependency injection container
│   ├── config.py                # Configuration management
│   ├── exceptions.py            # Custom exception hierarchy
│   ├── interfaces.py            # Protocol definitions
│   ├── document_processor.py    # .docx file processing
│   ├── claude_analyzer.py       # Claude AI integration
│   └── csv_exporter.py          # CSV output generation
├── test/                        # Comprehensive test suite
│   ├── test_main.py             # Main module tests
│   ├── test_cli.py              # CLI interface tests
│   ├── test_orchestrator.py     # Orchestrator tests
│   ├── test_container.py        # Container tests
│   ├── test_config.py           # Configuration tests
│   ├── test_exceptions.py       # Exception tests
│   ├── test_document_processor.py
│   ├── test_claude_analyzer.py
│   └── test_csv_exporter.py
├── data/                        # Input .docx files
├── output/                      # Generated reports
├── pyproject.toml               # Project configuration
├── .cursor/                     # Project rules and guidelines
└── README.md
```

### Test Coverage

The project maintains comprehensive test coverage:

| Module | Coverage | Status |
|--------|----------|--------|
| `claude_analyzer.py` | 91.92% | ✅ |
| `cli.py` | 100% | ✅ |
| `config.py` | 100% | ✅ |
| `container.py` | 97.01% | ✅ |
| `csv_exporter.py` | 97.67% | ✅ |
| `document_processor.py` | 80.44% | ✅ |
| `exceptions.py` | 100% | ✅ |
| `interfaces.py` | 100% | ✅ |
| `main.py` | 93.55% | ✅ |
| `orchestrator.py` | 95.20% | ✅ |

**Overall Coverage: 91.60%**

### Running Tests

Run the full test suite:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=news_contribution_check --cov-report=html
```

Run with detailed coverage:
```bash
pytest --cov=news_contribution_check --cov-report=term-missing
```

Run specific test modules:
```bash
pytest test/test_document_processor.py
pytest test/test_claude_analyzer.py
pytest test/test_orchestrator.py
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
black news_contribution_check/ test/
flake8 news_contribution_check/ test/
isort news_contribution_check/ test/
mypy news_contribution_check/
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:
```bash
pre-commit install
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Required. Your Anthropic Claude API key.

### Configuration Classes

The application uses class-based configuration with validation:

#### AppConfig
Main configuration class that combines all settings:
- API configuration (model, tokens, temperature)
- Processing settings (directories, limits)
- Validation and error handling

#### APIConfig
Claude AI specific settings:
- Model: `claude-sonnet-4-20250514` (Claude 4 Sonnet)
- Max tokens: 2000
- Temperature: 0.1 (for consistent results)

#### ProcessingConfig
File processing settings:
- Max description length: 300 characters
- Default data directory: `data/`
- Default output directory: `output/`

## Error Handling

The application implements a comprehensive error handling system:

### Custom Exception Hierarchy
- `NewsContributionCheckError`: Base exception class
- `ConfigurationError`: Configuration and setup issues
- `DocumentProcessingError`: File processing failures
- `ClaudeAPIError`: AI analysis failures
- `CSVExportError`: Output generation failures
- `ValidationError`: Data validation issues

### Error Recovery
- **Missing API key**: Clear error message with setup instructions
- **No .docx files**: Informative message about expected file location
- **Corrupted documents**: Individual file failures don't stop processing
- **API failures**: Graceful degradation with detailed error context
- **Invalid dates**: Fallback to default values as specified

## Performance Considerations

- **Large documents**: Articles are processed individually to manage memory
- **API rate limits**: Consider Anthropic's rate limits for bulk processing
- **Batch processing**: Multiple articles processed sequentially with progress indicators
- **Dependency caching**: Container caches instances for performance
- **Resource management**: Proper cleanup of file handles and connections

## Limitations

- Only supports .docx format (not .doc or other formats)
- Requires Claude AI API access (paid service)
- Date extraction relies on common patterns (may miss unusual formats)
- Company identification depends on explicit mentions (not implied references)

## Contributing

1. Follow all rules in `.cursor/rules/`
2. Maintain test coverage above 80% per module
3. Use conventional commit messages
4. Ensure all quality checks pass
5. Update documentation for new features
6. Follow SOLID principles and OOP best practices
7. Use dependency injection for new components

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues or questions:
1. Check the existing documentation
2. Review error messages and logs
3. Ensure API key is correctly configured  
4. Verify input file format matches expectations
5. Check test coverage for affected modules