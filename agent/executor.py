"""Executor — runs research tasks using tools (search + extract + analyze)."""
from typing import List, Dict, Callable, Optional
from .providers.base import BaseLLMProvider
from .tools.web_search import WebSearchTool
from .tools.content_extractor import ContentExtractorTool
from .prompts import get_analysis_prompt, AGENT_SYSTEM_PROMPT


class Executor:
    """Executes individual research tasks: search → extract → analyze."""

    def __init__(self, llm: BaseLLMProvider, max_search_results: int = 5,
                 max_pages: int = 3, max_content_chars: int = 6000,
                 max_analysis_tokens: int = 4096, compact_mode: bool = False):
        self.llm = llm
        self.searcher = WebSearchTool()
        self.extractor = ContentExtractorTool()
        self.max_results = max_search_results
        self.max_pages = max_pages
        self.max_content_chars = max_content_chars
        self.max_analysis_tokens = max_analysis_tokens
        self.compact_mode = compact_mode
        self.log_fn: Optional[Callable] = None

    def set_logger(self, fn: Callable):
        self.log_fn = fn

    def _log(self, phase: str, msg: str):
        if self.log_fn:
            self.log_fn(phase, msg)

    def execute_query(self, query: str) -> Dict:
        """
        Execute a single research query:
        1. Search the web
        2. Extract content from top results
        3. Analyze findings with LLM
        
        Returns dict with: query, analysis, sources
        """
        # Step 1: Search
        self._log("search", f"🔍 Searching: {query}")
        search_results = self.searcher.search(query, max_results=self.max_results)

        if not search_results:
            self._log("search", f"⚠ No results found for: {query}")
            return {
                "query": query,
                "analysis": "No search results found for this query.",
                "sources": [],
            }

        # Format search snippets (truncate for small models)
        max_snippet = 100 if self.compact_mode else 300
        search_text = "\n".join([
            f"- [{r['title']}]({r['url']})\n  {r['snippet'][:max_snippet]}"
            for r in search_results
        ])
        self._log("search", f"✅ Found {len(search_results)} results")

        # Step 2: Extract content from top URLs
        self._log("extract", f"📄 Extracting content from top {self.max_pages} sources...")
        urls = [r["url"] for r in search_results[:self.max_pages]]
        chars_per_page = 1500 if self.compact_mode else 3000
        extracted = self.extractor.extract_multiple(urls, max_chars_per_page=chars_per_page)

        web_content = ""
        sources = []
        for url, content in extracted.items():
            if content:
                title = next((r["title"] for r in search_results if r["url"] == url), url)
                web_content += f"\n--- SOURCE: {title} ({url}) ---\n{content}\n"
                sources.append(url)

        if not web_content:
            web_content = "No detailed content could be extracted. Use search snippets above."

        self._log("extract", f"✅ Extracted content from {len(extracted)} pages")

        # Step 3: Analyze with LLM (respect content limit)
        self._log("analyze", f"🧠 Analyzing findings...")
        analysis_prompt = get_analysis_prompt(
            query=query,
            search_results=search_text,
            web_content=web_content[:self.max_content_chars],
            compact=self.compact_mode,
        )

        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": analysis_prompt},
        ]

        analysis = self.llm.generate(messages, temperature=0.3,
                                     max_tokens=self.max_analysis_tokens)
        self._log("analyze", f"✅ Analysis complete")

        return {
            "query": query,
            "analysis": analysis,
            "sources": sources,
        }

    def execute_all(self, queries: List[str]) -> List[Dict]:
        """Execute all research queries sequentially."""
        results = []
        for i, query in enumerate(queries, 1):
            self._log("execute", f"📋 Task {i}/{len(queries)}")
            result = self.execute_query(query)
            results.append(result)
        return results
