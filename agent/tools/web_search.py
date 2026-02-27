"""Web Search Tool — uses DuckDuckGo (no API key required)."""
import requests
import urllib.parse
import re
from typing import List, Dict


class WebSearchTool:
    """
    Searches the web using DuckDuckGo HTML (no API key needed).
    Falls back to Google News RSS if DuckDuckGo is unavailable.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web and return a list of results.
        Each result has: title, url, snippet.
        """
        results = self._search_duckduckgo(query, max_results)
        if not results:
            results = self._search_google_rss(query, max_results)
        return results

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo HTML scraping."""
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {"User-Agent": self.USER_AGENT}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            results = []
            # Parse results from DDG HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select(".result"):
                title_tag = result.select_one(".result__title a")
                snippet_tag = result.select_one(".result__snippet")

                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                href = title_tag.get("href", "")

                # DDG wraps URLs in a redirect — extract actual URL
                if "uddg=" in href:
                    actual_url = urllib.parse.unquote(
                        href.split("uddg=")[1].split("&")[0]
                    )
                else:
                    actual_url = href

                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                results.append({
                    "title": title,
                    "url": actual_url,
                    "snippet": snippet,
                })

                if len(results) >= max_results:
                    break

            return results

        except Exception:
            return []

    def _search_google_rss(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Fallback: Search using Google News RSS feed."""
        try:
            import feedparser
            encoded_query = urllib.parse.quote(query)
            rss_url = (
                f"https://news.google.com/rss/search?"
                f"q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            )
            feed = feedparser.parse(rss_url)
            results = []
            for entry in feed.entries[:max_results]:
                results.append({
                    "title": entry.title,
                    "url": entry.link,
                    "snippet": entry.get("summary", ""),
                })
            return results
        except Exception:
            return []
