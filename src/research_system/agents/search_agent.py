from langchain.agents import create_agent
from research_system.models.model_selection import llm
from research_system.tools.tool import web_search


# Building the search agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )
