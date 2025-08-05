# Data Directory

This directory is where you should place your `.docx` files containing news articles for analysis.

## Usage

1. Place your Microsoft Word documents (`.docx` format) in this directory
2. The application will automatically process all `.docx` files found here
3. Supported formats:
   - News articles with standardized formatting
   - Articles separated by heading styles or section breaks
   - Documents containing publication sources and dates

## Example Structure

```
data/
├── news_articles_january.docx
├── news_articles_february.docx
└── quarterly_report.docx
```

## Security Note

**The contents of this directory are ignored by Git** to protect your data privacy. Your `.docx` files will never be committed to version control or shared publicly.

Only this README file is tracked in the repository to maintain the folder structure for new users.