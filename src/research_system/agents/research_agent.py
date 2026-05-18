from langchain.agents import create_agent
from research_system.models.model_selection import llm
from research_system.tools.tool import scrape_url


# Building the research agent
def build_research_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )
