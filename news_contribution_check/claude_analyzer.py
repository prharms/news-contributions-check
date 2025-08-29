"""Claude API integration for entity extraction and analysis."""

import json
import os
from typing import Dict, List, Optional

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .config import AppConfig
from .exceptions import ClaudeAPIError
from .document_processor import Article


class CompanyMention(BaseModel):
    """Represents a company or organization mention in an article."""

    company_name: str = Field(description="The exact name of the company or organization")
    description: str = Field(description="Brief description of the company's role in the article")


class ArticleAnalysis(BaseModel):
    """Analysis results for a single article."""

    article_title: str
    publication_source: str
    publication_date: str
    company_mentions: List[CompanyMention]


class ClaudeAnalyzer:
    """Analyzes articles using Claude API to extract company mentions."""

    def __init__(self, api_key: str, config: Optional[AppConfig] = None) -> None:
        """Initialize the Claude analyzer.

        Args:
            api_key: Anthropic API key
            config: Application configuration. If None, creates default config.

        Raises:
            ValueError: If API key is not provided
        """
        if not api_key:
            raise ValueError("API key is required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self._config = config or AppConfig()

    def analyze_article(self, article: Article) -> ArticleAnalysis:
        """Analyze a single article to extract company mentions.

        Args:
            article: The article to analyze

        Returns:
            Analysis results containing company mentions

        Raises:
            ClaudeAPIError: If analysis fails
        """
        try:
            import logging
            logger = logging.getLogger("news_contribution_check.claude_analyzer")
            
            logger.debug(f"Starting analysis of article: {article.title[:50]}...", extra={
                'operation': 'article_analysis',
                'article_title': article.title,
                'article_source': article.source,
                'article_date': article.date
            })
            
            prompt = self._create_analysis_prompt(article)
            response = self._call_claude_api(prompt)
            result = self._parse_response(article, response)
            
            logger.info(f"Successfully analyzed article: {article.title[:50]}...", extra={
                'operation': 'article_analysis',
                'article_title': article.title,
                'company_mentions_count': len(result.company_mentions),
                'status': 'success'
            })
            
            return result
        except Exception as e:
            import logging
            logger = logging.getLogger("news_contribution_check.claude_analyzer")
            logger.error(f"Failed to analyze article '{article.title}': {e}", extra={
                'operation': 'article_analysis',
                'article_title': article.title,
                'article_source': article.source,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'status': 'error'
            })
            raise ClaudeAPIError(f"Failed to analyze article '{article.title}': {e}", cause=e) from e

    def analyze_articles(self, articles: List[Article]) -> List[ArticleAnalysis]:
        """Analyze multiple articles to extract company mentions.

        Args:
            articles: List of articles to analyze

        Returns:
            List of analysis results
        """
        import logging
        logger = logging.getLogger("news_contribution_check.claude_analyzer")
        
        logger.info(f"Starting batch analysis of {len(articles)} articles", extra={
            'operation': 'batch_analysis',
            'total_articles': len(articles)
        })
        
        results = []
        successful_analyses = 0
        failed_analyses = 0
        
        for i, article in enumerate(articles, 1):
            try:
                logger.info(f"Analyzing article {i}/{len(articles)}: {article.title[:50]}...")
                analysis = self.analyze_article(article)
                results.append(analysis)
                successful_analyses += 1
            except Exception as e:
                logger.warning(f"Failed to analyze article '{article.title}': {e}", extra={
                    'operation': 'batch_analysis',
                    'article_index': i,
                    'article_title': article.title,
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                # Create empty analysis for failed articles
                results.append(
                    ArticleAnalysis(
                        article_title=article.title,
                        publication_source=article.source,
                        publication_date=article.date,
                        company_mentions=[],
                    )
                )
                failed_analyses += 1
        
        logger.info(f"Batch analysis completed: {successful_analyses} successful, {failed_analyses} failed", extra={
            'operation': 'batch_analysis',
            'total_articles': len(articles),
            'successful_analyses': successful_analyses,
            'failed_analyses': failed_analyses,
            'success_rate': successful_analyses / len(articles) if articles else 0
        })
        
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
(G) NOT THE NAME OF A NEWS ORGANIZATION
(H) NOT THE COPYRIGHT HOLDER LISTED IN THE ARTICLE'S COPYRIGHT INFORMATION
(I) NOT A POLITICAL PARTY OR POLITICAL COMMITTEE (e.g., "Democratic Party", "Republican Party", "Labour Party")

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
- Political parties or their committees (e.g., "Democratic Party", "Republican Party")
- Focus only on private sector organizations that are subjects of the news story, not sources reporting it

Remember: You are a forensic document analyst. Your analysis must be precise and exclude all government entities, media organizations, and political parties."""

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
                model=self._config.api.model,
                max_tokens=self._config.api.max_tokens,
                temperature=self._config.api.temperature,
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

            def _is_political_party(name: str) -> bool:
                n = name.strip().lower()
                if not n:
                    return False
                known = {
                    "democratic party",
                    "republican party",
                    "libertarian party",
                    "green party",
                    "labour party",
                    "conservative party",
                    "socialist party",
                    "communist party",
                    "people's party",
                    "national party",
                }
                if n in known:
                    return True
                if n.endswith(" party"):
                    return True
                # Common shorthand
                if n in {"democrats", "republicans"}:
                    return True
                return False

            def _is_copyright_holder(description: str) -> bool:
                d = (description or "").lower()
                triggers = ["copyright", "©", "all rights reserved", "rights to the article"]
                return any(t in d for t in triggers)

            company_mentions: List[CompanyMention] = []
            for mention_data in data["company_mentions"]:
                if not isinstance(mention_data, dict):
                    continue

                company_name = mention_data.get("company_name", "").strip()
                description = mention_data.get("description", "").strip()

                if not company_name:
                    continue

                # Enforce critical exclusions at parse-time
                if company_name.strip().lower() == (article.source or "").strip().lower():
                    # Exclude the publication itself
                    continue
                if _is_political_party(company_name):
                    continue
                if _is_copyright_holder(description):
                    continue

                # Truncate description if too long
                if len(description) > self._config.max_description_length:
                    description = description[:self._config.max_description_length - 3] + "..."

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