from dataclasses import dataclass

import pytest

from research_system.pipelines import research_pipeline


@dataclass
class FakeMessage:
    content: str


class FakeAgent:
    def __init__(self, content: str):
        self.content = content
        self.calls = []

    def invoke(self, payload: dict) -> dict:
        self.calls.append(payload)
        return {"messages": [FakeMessage(content=self.content)]}


class FakeChain:
    def __init__(self, output: str):
        self.output = output
        self.calls = []

    def invoke(self, payload: dict) -> str:
        self.calls.append(payload)
        return self.output


@pytest.mark.integration
def test_run_research_pipeline_orchestrates_agents_and_chains(monkeypatch):
    search_agent = FakeAgent(
        "Title: Example Source\nURL: https://example.com\nSnippet: Useful context"
    )
    reader_agent = FakeAgent("Detailed scraped content from the selected source.")
    writer_chain = FakeChain("Final structured report")
    critic_chain = FakeChain("Score: 8/10\n\nOne line verdict:\nUseful first draft.")

    monkeypatch.setattr(research_pipeline, "build_search_agent", lambda: search_agent)
    monkeypatch.setattr(research_pipeline, "build_research_agent", lambda: reader_agent)
    monkeypatch.setattr(research_pipeline, "writer_chain", writer_chain)
    monkeypatch.setattr(research_pipeline, "critic_chain", critic_chain)

    result = research_pipeline.run_research_pipeline("agentic AI platforms")

    assert result["search_results"] == search_agent.content
    assert result["scraped_content"] == reader_agent.content
    assert result["report"] == "Final structured report"
    assert result["feedback"].startswith("Score: 8/10")

    assert "agentic AI platforms" in search_agent.calls[0]["messages"][0][1]
    assert "Example Source" in reader_agent.calls[0]["messages"][0][1]
    assert writer_chain.calls[0]["topic"] == "agentic AI platforms"
    assert "DETAILED SCRAPED CONTENT" in writer_chain.calls[0]["research"]
    assert critic_chain.calls[0]["report"] == "Final structured report"
