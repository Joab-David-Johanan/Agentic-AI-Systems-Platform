from langchain.agents import create_agent

from research_system.middleware import DEFAULT_AGENT_MIDDLEWARE
from research_system.models.model_selection import get_llm
from research_system.tools.tool import scrape_url


# Building the research agent
def build_research_agent():
    return create_agent(
        model=get_llm(),
        tools=[scrape_url],
        middleware=DEFAULT_AGENT_MIDDLEWARE,
    )


def build_langgraph_research_agent():
    from langgraph.prebuilt import create_react_agent

    return create_react_agent(
        model=get_llm(),
        tools=[scrape_url],
    )
