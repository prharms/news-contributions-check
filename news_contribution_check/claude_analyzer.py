"""Claude API integration for entity extraction and analysis."""

import json
import os
from typing import Dict, List, Optional

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE, MAX_DESCRIPTION_LENGTH
from .exceptions import ClaudeAPIError
from .document_processor import Article


class CompanyMention(BaseModel):
    """Represents a company or organization mention in an article."""

    company_name: str = Field(description="The exact name of the company or organization")
    description: str = Field(
        max_length=MAX_DESCRIPTION_LENGTH, description="Brief description of the company's role in the article"
    )


class ArticleAnalysis(BaseModel):
    """Analysis results for a single article."""

    article_title: str
    publication_source: str
    publication_date: str
    company_mentions: List[CompanyMention]


class ClaudeAnalyzer:
    """Analyzes articles using Claude API to extract company mentions."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the Claude analyzer.

        Args:
            api_key: Anthropic API key. If None, loads from environment.

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "Anthropic API key is required. "
                "Set ANTHROPIC_API_KEY environment variable or provide api_key parameter."
            )

        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze_article(self, article: Article) -> ArticleAnalysis:
        """Analyze a single article to extract company mentions.

        Args:
            article: The article to analyze

        Returns:
            Analysis results containing company mentions

        Raises:
            ValueError: If analysis fails
        """
        try:
            prompt = self._create_analysis_prompt(article)
            response = self._call_claude_api(prompt)
            return self._parse_response(article, response)
        except Exception as e:
            raise ValueError(f"Failed to analyze article '{article.title}': {e}") from e

    def analyze_articles(self, articles: List[Article]) -> List[ArticleAnalysis]:
        """Analyze multiple articles to extract company mentions.

        Args:
            articles: List of articles to analyze

        Returns:
            List of analysis results
        """
        results = []
        for i, article in enumerate(articles, 1):
            try:
                print(f"Analyzing article {i}/{len(articles)}: {article.title[:50]}...")
                analysis = self.analyze_article(article)
                results.append(analysis)
            except Exception as e:
                print(f"Warning: Failed to analyze article '{article.title}': {e}")
                # Create empty analysis for failed articles
                results.append(
                    ArticleAnalysis(
                        article_title=article.title,
                        publication_source=article.source,
                        publication_date=article.date,
                        company_mentions=[],
                    )
                )
        return results

    def _create_analysis_prompt(self, article: Article) -> str:
        """Create the analysis prompt for Claude.

        Args:
            article: The article to analyze

        Returns:
            Formatted prompt string
        """
        return f"""You are acting as a forensic document analyst. Your responses must meet the standards to be included as documentary evidence in litigation. Zero creativity is allowed. You must be precise, accurate, and strictly follow the guidelines below.

Please analyze the following news article and identify all companies and organizations explicitly mentioned by name. For each company or organization found, provide:

1. The exact company/organization name as mentioned in the article
2. A brief description (maximum 300 characters) of how the company or organization is involved or mentioned in the article

Article Details:
Title: {article.title}
Source: {article.source}
Date: {article.date}
Content: {article.content}

MANDATORY CHECKLIST - Before returning any value as a company/organization name, you MUST verify that the entity is:
(A) NOT A CITY
(B) NOT A COUNTY  
(C) NOT A STATE
(D) NOT THE FEDERAL GOVERNMENT
(E) NOT THE NAME OF A NEWSPAPER
(F) NOT THE NAME OF OTHER NEWS MEDIA

If ANY of these conditions are true, DO NOT include the entity as a company/organization name.

Please respond with a JSON object in this exact format:
{{
    "company_mentions": [
        {{
            "company_name": "Exact Company Name",
            "description": "Brief description of company's role in the article (max 300 chars)"
        }}
    ]
}}

Important guidelines:
- Only include companies and organizations that are explicitly named in the article
- Do not include generic terms like "the company" or "the organization" unless they are proper names
- Keep descriptions factual and concise
- If no companies or organizations are mentioned, return an empty array
- Ensure the JSON is valid and properly formatted

CRITICAL EXCLUSIONS - NEVER include:
- The news publication/newspaper name ("{article.source}") as a company mention
- Other news media outlets as companies unless they are the actual subject of the story (not just cited as sources)
- The author's name or byline information
- Any government entities (cities, counties, states, federal agencies)
- Focus only on private sector organizations that are subjects of the news story, not sources reporting it

Remember: You are a forensic document analyst. Your analysis must be precise and exclude all government entities and media organizations."""

    def _call_claude_api(self, prompt: str) -> str:
        """Call the Claude API with the given prompt.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Claude's response text

        Raises:
            Exception: If API call fails
        """
        try:
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                temperature=CLAUDE_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            
            # Handle Claude 4's new refusal stop reason
            if hasattr(message, 'stop_reason') and message.stop_reason == 'refusal':
                raise Exception("Claude refused to process the request for safety reasons")
            
            return message.content[0].text
        except Exception as e:
            raise ClaudeAPIError(f"Claude API call failed: {e}", cause=e) from e

    def _parse_response(self, article: Article, response: str) -> ArticleAnalysis:
        """Parse Claude's response into structured data.

        Args:
            article: The original article
            response: Claude's response text

        Returns:
            Parsed analysis results

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            # Validate structure
            if "company_mentions" not in data:
                raise ValueError("Missing 'company_mentions' in response")

            company_mentions = []
            for mention_data in data["company_mentions"]:
                if not isinstance(mention_data, dict):
                    continue

                company_name = mention_data.get("company_name", "").strip()
                description = mention_data.get("description", "").strip()

                if not company_name:
                    continue

                # Truncate description if too long
                if len(description) > MAX_DESCRIPTION_LENGTH:
                    description = description[:MAX_DESCRIPTION_LENGTH - 3] + "..."

                company_mentions.append(
                    CompanyMention(company_name=company_name, description=description)
                )

            return ArticleAnalysis(
                article_title=article.title,
                publication_source=article.source,
                publication_date=article.date,
                company_mentions=company_mentions,
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to parse response: {e}") from e