"""Web search tool using DuckDuckGo."""

from typing import List, Dict, Any
import json


def search_web(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        Search results as formatted string
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "Error: duckduckgo-search not installed. Install with: pip install duckduckgo-search"

    try:
        results = []
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            for i, result in enumerate(search_results, 1):
                results.append(
                    f"{i}. {result.get('title', 'No title')}\n"
                    f"   URL: {result.get('link', 'No URL')}\n"
                    f"   Description: {result.get('body', 'No description')}\n"
                )

        if not results:
            return f"No results found for: {query}"

        return "Search Results:\n" + "\n".join(results)

    except Exception as e:
        return f"Error performing search: {str(e)}"


def search_web_json(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web and return as JSON.

    Args:
        query: Search query
        max_results: Maximum results

    Returns:
        List of results as dicts
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return []

    results = []
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            for result in search_results:
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "description": result.get("body", ""),
                    }
                )
    except Exception:
        pass

    return results


def search_news(query: str, max_results: int = 5) -> str:
    """Search for news articles.

    Args:
        query: Search query
        max_results: Maximum results

    Returns:
        News results
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "Error: duckduckgo-search not installed"

    try:
        results = []
        with DDGS() as ddgs:
            news_results = ddgs.news(query, max_results=max_results)
            for i, result in enumerate(news_results, 1):
                results.append(
                    f"{i}. {result.get('title', 'No title')}\n"
                    f"   Date: {result.get('date', 'Unknown')}\n"
                    f"   URL: {result.get('link', 'No URL')}\n"
                )

        return "News Results:\n" + "\n".join(results) if results else "No news found"

    except Exception as e:
        return f"Error searching news: {str(e)}"
