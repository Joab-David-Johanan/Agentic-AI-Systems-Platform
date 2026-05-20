from collections.abc import Callable
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from research_system.models.model_selection import get_llm

# writer_chain

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""",
        ),
    ]
)


def build_writer_chain():
    return writer_prompt | get_llm() | StrOutputParser()


# critic_chain

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest and specific.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)


def build_critic_chain():
    return critic_prompt | get_llm() | StrOutputParser()


class LazyChain:
    """Build an LLM chain only when it is first invoked."""

    def __init__(self, builder: Callable[[], Any]):
        self._builder = builder
        self._chain: Any | None = None

    def invoke(self, payload: dict) -> str:
        if self._chain is None:
            self._chain = self._builder()
        chain = self._chain
        return chain.invoke(payload)


writer_chain = LazyChain(build_writer_chain)
critic_chain = LazyChain(build_critic_chain)
