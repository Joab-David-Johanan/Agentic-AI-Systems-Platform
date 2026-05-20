import requests

from research_system.tools import tool as tool_module


class FakeTavilyClient:
    def search(self, query: str, max_results: int) -> dict:
        assert query == "agentic ai"
        assert max_results == 5
        return {
            "results": [
                {
                    "title": "Agentic AI Systems",
                    "url": "https://example.com/agentic-ai",
                    "content": "A" * 350,
                },
                {
                    "title": "Reliable LLM Workflows",
                    "url": "https://example.com/reliable-llm",
                    "content": "Short summary",
                },
            ]
        }


class FakeResponse:
    text = "<html><body><article>ignored html</article></body></html>"

    def raise_for_status(self) -> None:
        return None


def test_web_search_formats_tavily_results(monkeypatch):
    monkeypatch.setattr(tool_module, "tavily", FakeTavilyClient())

    result = tool_module.web_search.func("agentic ai")

    assert "Title: Agentic AI Systems" in result
    assert "URL: https://example.com/agentic-ai" in result
    assert "Snippet:" in result
    assert "------" in result
    assert len(result) < 900


def test_scrape_url_uses_trafilatura_first(monkeypatch):
    extracted = "This is clean extracted article text. " * 20

    monkeypatch.setattr(
        tool_module.requests, "get", lambda *args, **kwargs: FakeResponse()
    )
    monkeypatch.setattr(
        tool_module.trafilatura, "extract", lambda *args, **kwargs: extracted
    )

    result = tool_module.scrape_url.func("https://example.com/article")

    assert result.startswith("This is clean extracted article text.")
    assert "\n" not in result
    assert len(result) <= 5000


def test_scrape_url_handles_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(tool_module.requests, "get", raise_timeout)

    result = tool_module.scrape_url.func("https://example.com/slow")

    assert result == "Request timed out while scraping the URL."
