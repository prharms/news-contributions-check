"""Tests for claude_analyzer module."""

import json
from unittest.mock import Mock, patch

import pytest

from src.claude_analyzer import ArticleAnalysis, ClaudeAnalyzer, CompanyMention
from src.document_processor import Article


class TestClaudeAnalyzer:
    """Test cases for ClaudeAnalyzer class."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_initialization_with_env_var(self) -> None:
        """Test analyzer initialization with environment variable."""
        with patch('src.claude_analyzer.anthropic.Anthropic') as mock_anthropic:
            analyzer = ClaudeAnalyzer()
            mock_anthropic.assert_called_once_with(api_key='test-api-key')

    def test_initialization_with_api_key(self) -> None:
        """Test analyzer initialization with provided API key."""
        with patch('src.claude_analyzer.anthropic.Anthropic') as mock_anthropic:
            analyzer = ClaudeAnalyzer(api_key='provided-key')
            mock_anthropic.assert_called_once_with(api_key='provided-key')

    @patch.dict('os.environ', {}, clear=True)
    @patch('src.claude_analyzer.load_dotenv')
    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_initialization_without_api_key(self, mock_anthropic: Mock, mock_load_dotenv: Mock) -> None:
        """Test analyzer initialization without API key raises error."""
        # Mock load_dotenv to not load anything
        mock_load_dotenv.return_value = None
        with pytest.raises(ValueError, match="Anthropic API key is required"):
            ClaudeAnalyzer()

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_create_analysis_prompt(self, mock_anthropic: Mock) -> None:
        """Test analysis prompt creation."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content with Apple Inc. and Microsoft Corporation.",
            raw_text="Raw text"
        )
        
        prompt = analyzer._create_analysis_prompt(article)
        
        assert "Test Title" in prompt
        assert "Test Source" in prompt
        assert "2024-01-15" in prompt
        assert "Apple Inc. and Microsoft Corporation" in prompt
        assert "company_mentions" in prompt
        assert "JSON" in prompt

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_call_claude_api_success(self, mock_anthropic: Mock) -> None:
        """Test successful Claude API call."""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text='{"company_mentions": []}')]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        analyzer = ClaudeAnalyzer(api_key='test-key')
        response = analyzer._call_claude_api("test prompt")
        
        assert response == '{"company_mentions": []}'
        mock_client.messages.create.assert_called_once()

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_call_claude_api_failure(self, mock_anthropic: Mock) -> None:
        """Test Claude API call failure."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        with pytest.raises(Exception, match="Claude API call failed"):
            analyzer._call_claude_api("test prompt")

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_parse_response_success(self, mock_anthropic: Mock) -> None:
        """Test successful response parsing."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        response = '''
        Here is the analysis:
        {
            "company_mentions": [
                {
                    "company_name": "Apple Inc.",
                    "description": "Technology company mentioned in the article"
                },
                {
                    "company_name": "Microsoft Corporation",
                    "description": "Software company involved in the news"
                }
            ]
        }
        '''
        
        analysis = analyzer._parse_response(article, response)
        
        assert analysis.article_title == "Test Title"
        assert analysis.publication_source == "Test Source"
        assert analysis.publication_date == "2024-01-15"
        assert len(analysis.company_mentions) == 2
        assert analysis.company_mentions[0].company_name == "Apple Inc."
        assert analysis.company_mentions[1].company_name == "Microsoft Corporation"

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_parse_response_no_json(self, mock_anthropic: Mock) -> None:
        """Test response parsing with no JSON."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        response = "No JSON in this response"
        
        with pytest.raises(ValueError, match="No JSON found in response"):
            analyzer._parse_response(article, response)

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_parse_response_invalid_json(self, mock_anthropic: Mock) -> None:
        """Test response parsing with invalid JSON."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        response = '{"invalid": json,}'
        
        with pytest.raises(ValueError, match="Invalid JSON in response"):
            analyzer._parse_response(article, response)

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_parse_response_missing_company_mentions(self, mock_anthropic: Mock) -> None:
        """Test response parsing with missing company_mentions field."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        response = '{"some_other_field": []}'
        
        with pytest.raises(ValueError, match="Missing 'company_mentions' in response"):
            analyzer._parse_response(article, response)

    @patch('src.claude_analyzer.anthropic.Anthropic')
    def test_parse_response_long_description(self, mock_anthropic: Mock) -> None:
        """Test response parsing with long description gets truncated."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        long_description = "A" * 350  # Longer than 300 chars
        response = f'''{{
            "company_mentions": [
                {{
                    "company_name": "Test Company",
                    "description": "{long_description}"
                }}
            ]
        }}'''
        
        analysis = analyzer._parse_response(article, response)
        
        assert len(analysis.company_mentions[0].description) == 300
        assert analysis.company_mentions[0].description.endswith("...")

    @patch('src.claude_analyzer.anthropic.Anthropic')
    @patch.object(ClaudeAnalyzer, '_call_claude_api')
    @patch.object(ClaudeAnalyzer, '_parse_response')
    def test_analyze_article_success(self, mock_parse: Mock, mock_call: Mock, mock_anthropic: Mock) -> None:
        """Test successful article analysis."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        article = Article(
            title="Test Title",
            source="Test Source",
            date="2024-01-15",
            content="Test content",
            raw_text="Raw text"
        )
        
        mock_call.return_value = "mock response"
        mock_analysis = ArticleAnalysis(
            article_title="Test Title",
            publication_source="Test Source",
            publication_date="2024-01-15",
            company_mentions=[]
        )
        mock_parse.return_value = mock_analysis
        
        result = analyzer.analyze_article(article)
        
        assert result == mock_analysis
        mock_call.assert_called_once()
        mock_parse.assert_called_once_with(article, "mock response")

    @patch('src.claude_analyzer.anthropic.Anthropic')
    @patch.object(ClaudeAnalyzer, 'analyze_article')
    def test_analyze_articles_success(self, mock_analyze: Mock, mock_anthropic: Mock) -> None:
        """Test successful multiple article analysis."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        articles = [
            Article(title="Article 1", source="Source 1", date="2024-01-15", content="Content 1", raw_text="Raw 1"),
            Article(title="Article 2", source="Source 2", date="2024-01-16", content="Content 2", raw_text="Raw 2"),
        ]
        
        mock_analyses = [
            ArticleAnalysis(article_title="Article 1", publication_source="Source 1", publication_date="2024-01-15", company_mentions=[]),
            ArticleAnalysis(article_title="Article 2", publication_source="Source 2", publication_date="2024-01-16", company_mentions=[]),
        ]
        
        mock_analyze.side_effect = mock_analyses
        
        results = analyzer.analyze_articles(articles)
        
        assert len(results) == 2
        assert results == mock_analyses
        assert mock_analyze.call_count == 2

    @patch('src.claude_analyzer.anthropic.Anthropic')
    @patch.object(ClaudeAnalyzer, 'analyze_article')
    @patch('builtins.print')
    def test_analyze_articles_with_failure(self, mock_print: Mock, mock_analyze: Mock, mock_anthropic: Mock) -> None:
        """Test multiple article analysis with one failure."""
        analyzer = ClaudeAnalyzer(api_key='test-key')
        
        articles = [
            Article(title="Article 1", source="Source 1", date="2024-01-15", content="Content 1", raw_text="Raw 1"),
            Article(title="Article 2", source="Source 2", date="2024-01-16", content="Content 2", raw_text="Raw 2"),
        ]
        
        mock_analysis = ArticleAnalysis(
            article_title="Article 1",
            publication_source="Source 1",
            publication_date="2024-01-15",
            company_mentions=[]
        )
        
        mock_analyze.side_effect = [mock_analysis, Exception("Analysis failed")]
        
        results = analyzer.analyze_articles(articles)
        
        assert len(results) == 2
        assert results[0] == mock_analysis
        assert results[1].article_title == "Article 2"
        assert len(results[1].company_mentions) == 0  # Empty due to failure


class TestCompanyMention:
    """Test cases for CompanyMention model."""

    def test_company_mention_creation(self) -> None:
        """Test company mention model creation."""
        mention = CompanyMention(
            company_name="Apple Inc.",
            description="Technology company"
        )
        
        assert mention.company_name == "Apple Inc."
        assert mention.description == "Technology company"


class TestArticleAnalysis:
    """Test cases for ArticleAnalysis model."""

    def test_article_analysis_creation(self) -> None:
        """Test article analysis model creation."""
        mentions = [
            CompanyMention(company_name="Apple Inc.", description="Tech company"),
            CompanyMention(company_name="Microsoft", description="Software company")
        ]
        
        analysis = ArticleAnalysis(
            article_title="Test Article",
            publication_source="Test Source",
            publication_date="2024-01-15",
            company_mentions=mentions
        )
        
        assert analysis.article_title == "Test Article"
        assert analysis.publication_source == "Test Source"
        assert analysis.publication_date == "2024-01-15"
        assert len(analysis.company_mentions) == 2