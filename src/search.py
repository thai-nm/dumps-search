"""Search engine implementation for ExamTopics PDF Scraper."""

import logging
import time
from typing import List, Optional
from urllib.parse import urlparse

from ddgs import DDGS


class SearchEngine:
    """Handles DuckDuckGo search operations for ExamTopics URLs."""

    def __init__(
        self, max_results: int = 10, retry_attempts: int = 3, retry_delay: float = 1.0
    ):
        """Initialize the search engine.

        Args:
            max_results: Maximum number of search results to retrieve
            retry_attempts: Number of retry attempts for failed searches
            retry_delay: Delay between retry attempts in seconds
        """
        self.max_results = max_results
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)

    def search_question(
        self, keyword: str, title: str, url_substring: str
    ) -> Optional[str]:
        """Search for a specific question and return the first valid ExamTopics URL.

        Uses DuckDuckGo advanced search syntax:
        site:examtopics.com title:"<title>" "<keyword>"

        Args:
            keyword: Search keyword/phrase
            title: Page title to search for (from HTML title tag)
            url_substring: Required substring in the URL to validate results

        Returns:
            First valid ExamTopics URL or None if no valid URL found
        """
        # Construct advanced search query using DuckDuckGo syntax
        search_query = f'site:examtopics.com title:{title} "{keyword}"'

        self.logger.debug(f"Searching with query: {search_query}")

        try:
            results = self._perform_search(search_query)
            if not results:
                self.logger.warning(
                    f"No search results found for query: {search_query}"
                )
                return None

            valid_url = self.get_first_valid_url(results, url_substring)
            if valid_url:
                self.logger.debug(f"Found valid URL: {valid_url}")
            else:
                self.logger.warning(f"No valid URLs found for query: {search_query}")

            return valid_url

        except Exception as e:
            self.logger.error(f"Search failed for query '{search_query}': {str(e)}")
            return None

    def _perform_search(self, query: str) -> List[dict]:
        """Perform the actual search with retry logic.

        Args:
            query: Search query string

        Returns:
            List of search result dictionaries

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.retry_attempts):
            try:
                self.logger.debug(f"Search attempt {attempt + 1} for query: {query}")

                results = list(
                    DDGS().text(
                        query,
                        max_results=self.max_results,
                        safesearch="off",
                        backend="google",
                    )
                )

                self.logger.debug(f"Retrieved {len(results)} search results")
                return results

            except Exception as e:
                last_exception = e
                self.logger.warning(f"Search attempt {attempt + 1} failed: {str(e)}")

                if attempt < self.retry_attempts - 1:
                    self.logger.debug(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

        # If we get here, all attempts failed
        raise Exception(
            f"All {self.retry_attempts} search attempts failed. Last error: {str(last_exception)}"
        )

    def get_first_valid_url(
        self, results: List[dict], url_substring: str
    ) -> Optional[str]:
        """Extract the first valid URL from search results.

        Args:
            results: List of search result dictionaries
            url_substring: Required substring to validate URLs

        Returns:
            First valid URL or None if no valid URL found
        """
        for result in results:
            url = result.get("href")
            if url and self.validate_url(url, url_substring):
                return url

        return None

    def validate_url(self, url: str, url_substring: str) -> bool:
        """Check if URL belongs to the target exam.

        Args:
            url: URL to validate
            url_substring: Required substring in the URL

        Returns:
            True if URL is valid, False otherwise
        """
        if not url or not url_substring:
            return False

        try:
            # Parse URL to ensure it's valid
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # Check if URL contains the required substring
            if url_substring.lower() in url.lower():
                self.logger.debug(f"URL validated: {url}")
                return True
            else:
                self.logger.debug(
                    f"URL rejected (missing substring '{url_substring}'): {url}"
                )
                return False

        except Exception as e:
            self.logger.debug(f"URL validation failed for '{url}': {str(e)}")
            return False

    def get_search_results(self, query: str) -> List[dict]:
        """Get all search results for a query (for debugging/testing).

        Args:
            query: Search query string

        Returns:
            List of all search result dictionaries
        """
        try:
            return self._perform_search(query)
        except Exception as e:
            self.logger.error(f"Failed to get search results for '{query}': {str(e)}")
            return []
