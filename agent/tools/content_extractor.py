"""Content Extractor Tool — scrapes and extracts text from web pages."""
import requests
from typing import Optional
from bs4 import BeautifulSoup


class ContentExtractorTool:
    """
    Extracts readable text content from web pages.
    Handles errors gracefully and returns clean text.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def extract(self, url: str, max_chars: int = 5000) -> Optional[str]:
        """
        Extract text content from a URL.
        Returns cleaned text limited to max_chars, or None on failure.
        """
        try:
            # Skip obviously bad URLs
            if not url.startswith("http") or "duckduckgo.com" in url:
                return None

            headers = {"User-Agent": self.USER_AGENT}
            response = requests.get(url, headers=headers, timeout=15,
                                    allow_redirects=True)
            response.raise_for_status()

            # Skip non-HTML responses
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text" not in content_type:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script, style, nav, footer elements
            for tag in soup(["script", "style", "nav", "footer", "header",
                             "aside", "form", "iframe", "noscript", "svg",
                             "button", "input", "select"]):
                tag.decompose()

            # Try to find main content areas first
            main_content = (
                soup.find("main") or
                soup.find("article") or
                soup.find("div", {"class": lambda x: x and "content" in x.lower()}) or
                soup.find("div", {"id": lambda x: x and "content" in x.lower()}) or
                soup.body or
                soup
            )

            # Extract text from paragraphs for cleaner output
            paragraphs = main_content.find_all(["p", "h1", "h2", "h3", "h4", "li", "td"])
            if paragraphs:
                text = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
            else:
                text = main_content.get_text(separator="\n", strip=True)

            # Fallback: if paragraph extraction got too little, use full text
            if len(text) < 100:
                text = (soup.body or soup).get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 10]
            clean_text = "\n".join(lines)

            return clean_text[:max_chars] if clean_text else None

        except Exception:
            return None

    def extract_multiple(self, urls: list, max_chars_per_page: int = 3000) -> dict:
        """Extract content from multiple URLs. Returns {url: content}."""
        results = {}
        for url in urls:
            content = self.extract(url, max_chars=max_chars_per_page)
            if content:
                results[url] = content
        return results
