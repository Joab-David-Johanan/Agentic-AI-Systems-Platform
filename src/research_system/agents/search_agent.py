from langchain.agents import create_agent

from research_system.middleware import DEFAULT_AGENT_MIDDLEWARE
from research_system.models.model_selection import get_llm
from research_system.tools.tool import web_search


# Building the search agent
def build_search_agent():
    return create_agent(
        model=get_llm(),
        tools=[web_search],
        middleware=DEFAULT_AGENT_MIDDLEWARE,
    )


def build_langgraph_search_agent():
    from langgraph.prebuilt import create_react_agent

    return create_react_agent(
        model=get_llm(),
        tools=[web_search],
    )
