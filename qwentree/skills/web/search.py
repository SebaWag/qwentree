"""🌐 web/search — Web scraping and search capabilities."""

from qwentree.core.qwen_client import qwen
import httpx
from bs4 import BeautifulSoup


def search(query: str, max_results: int = 5) -> dict:
    """Search the web for information."""
    try:
        if not query or not query.strip():
            return {"success": False, "error": "Empty query", "query": query}
        headers = {
            "User-Agent": "QwenTree/1.0 (AI Agent; +https://wagnersolutionsai.com)"
        }
        resp = httpx.get(
            f"https://html.duckduckgo.com/html/?q={query}",
            headers=headers,
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for result in soup.select(".result")[:max_results]:
            title_el = result.select_one(".result__title a")
            snippet_el = result.select_one(".result__snippet")
            if title_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": title_el.get("href", ""),
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })
        return {
            "success": True,
            "query": query,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}


def fetch(url: str) -> dict:
    """Fetch and extract content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        }
        resp = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        title = soup.title.string if soup.title else "No title"
        text = soup.get_text(separator="\n", strip=True)
        text = "\n".join(line for line in text.splitlines() if line.strip())
        if len(text) > 10000:
            text = text[:10000] + "\n\n...[truncated]"
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": text,
            "content_length": len(text),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}
