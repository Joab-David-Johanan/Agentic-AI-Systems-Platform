# Iterations

This file is a living architecture journal for the project.

The goal is to document each iteration of the system as it evolves:

- what the current control flow is
- why each file/layer exists
- what design problem the current version solves
- what is still weak or missing
- what the next iteration should improve

---

## Iteration 1: Baseline Agentic Research Workflow

### What exists in this iteration?

Iteration 1 implements the first working version of the platform: a research workflow built from tools, agents, model factories, prompt chains, and a pipeline.

The current workflow is:

```text
user topic
-> search agent
-> web_search tool
-> search results
-> research agent
-> scrape_url tool
-> scraped content
-> writer chain
-> report
-> critic chain
-> feedback
-> final state dictionary
```

This is not yet a full production-grade agentic platform. It is the first vertical slice proving that the basic layers can talk to each other.

### Current control flow

The main orchestration lives in:

```text
src/research_system/pipelines/research_pipeline.py
```

The pipeline calls the system in this order:

1. Build the search agent.
2. Ask it to find recent and reliable information about the topic.
3. Save the search result into the pipeline state.
4. Build the research agent.
5. Ask it to select a useful URL from search results and scrape deeper content.
6. Save scraped content into the pipeline state.
7. Combine search results and scraped content.
8. Send the combined research into the writer chain.
9. Save the generated report.
10. Send the report into the critic chain.
11. Save the feedback.
12. Return the full state dictionary.

Current state shape:

```python
{
    "search_results": "...",
    "scraped_content": "...",
    "report": "...",
    "feedback": "...",
}
```

Why this exists:

- It gives the project an end-to-end path.
- It proves the tool layer, agent layer, chain layer, and pipeline layer can work together.
- It creates a simple baseline before moving to LangGraph, retries, state typing, evaluation, and observability.

### Layer 1: Tools

File:

```text
src/research_system/tools/tool.py
```

Current tools:

```python
web_search
scrape_url
```

What they do:

- `web_search` uses Tavily to search the web.
- `scrape_url` downloads a web page and extracts readable content.

Why `@tool` exists:

```python
@tool
def web_search(query: str) -> str:
    ...
```

The `@tool` decorator converts a normal Python function into a LangChain-compatible tool.

That gives the function:

- tool metadata
- a standard `.invoke()` interface
- compatibility with LangChain agents
- a description agents can use when deciding what tool to call

Why this layer exists:

- Tools are the system's controlled interface to the outside world.
- Agents should not directly contain scraping or API logic.
- Keeping tools separate makes them easier to test, reuse, replace, and monitor.

Current weakness:

- Tool outputs are plain strings.
- There is no structured schema for URLs, titles, snippets, timestamps, source quality, or errors.
- There is no retry or fallback logic.
- Search and scraping are not cached.

Iteration 2 improvement:

- Return structured data instead of plain strings.
- Add retries, timeouts, and source metadata.
- Add source deduplication and ranking.

### Layer 2: Model Selection

File:

```text
src/research_system/models/model_selection.py
```

Current model functions:

```python
get_openai_llm()
get_groq_llm()
get_llm()
```

What changed:

Previously, the model was created immediately at import time:

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

That meant importing a file could create the model immediately.

Problem:

- Imports could require API credentials.
- Tests could fail before they even mocked the model.
- CI could fail because model initialization happened too early.
- Importing code had side effects.

Current design:

```python
@lru_cache(maxsize=1)
def get_openai_llm():
    from langchain_openai import ChatOpenAI

    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    return ChatOpenAI(model=model_name, temperature=0)
```

What `@lru_cache(maxsize=1)` does:

```text
first call -> create the model
later calls -> reuse the same model instance
```

Why this exists:

- Model creation is lazy.
- Imports stay lightweight.
- CI and tests can import modules safely.
- The same model object can be reused instead of recreated repeatedly.

Provider routing:

```python
def get_llm(provider: str | None = None):
    selected_provider = provider or os.getenv("LLM_PROVIDER") or "openai"
```

Current supported providers:

```text
openai
groq
```

Environment variables:

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL_NAME=gpt-4o-mini

LLM_PROVIDER=groq
GROQ_API_KEY=
GROQ_MODEL_NAME=llama-3.1-8b-instant
```

Why this layer exists:

- The rest of the app should not care whether the model is OpenAI, Groq, or another provider.
- Provider-specific code stays in one file.
- Future model switching becomes easier.

Current weakness:

- Provider config is still simple environment-variable logic.
- There is no validation for missing API keys.
- There is no fallback chain if one provider fails.
- There is no model capability registry.

Iteration 2 improvement:

- Add typed settings/config.
- Validate required environment variables at runtime.
- Add fallback provider support.
- Track model name, provider, token usage, and cost.

### Layer 3: Agents

Files:

```text
src/research_system/agents/search_agent.py
src/research_system/agents/research_agent.py
```

Current LangChain agent builders:

```python
build_search_agent()
build_research_agent()
```

What they do:

- `build_search_agent()` creates an agent with the web search tool.
- `build_research_agent()` creates an agent with the scraping tool.

Current pattern:

```python
return create_agent(
    model=get_llm(),
    tools=[web_search],
)
```

Why this exists:

- Agents combine model reasoning with tool access.
- Each agent gets only the tools needed for its role.
- This keeps responsibilities separated.

Current LangGraph extension builders:

```python
build_langgraph_search_agent()
build_langgraph_research_agent()
```

What they do:

- They use `langgraph.prebuilt.create_react_agent`.
- They are not yet wired into the main pipeline.
- They exist as a migration path toward graph-based orchestration.

Why this matters:

- LangChain agents are useful for early prototyping.
- LangGraph is better for explicit state, control flow, retries, loops, and production agent workflows.

Current weakness:

- Agents are created every time the pipeline runs.
- Agent roles are defined mostly through user prompts, not strong system prompts.
- There is no graph-level control over retries or tool failures.
- There is no typed state.

Iteration 2 improvement:

- Move orchestration into LangGraph.
- Define explicit graph nodes: search, rank, scrape, write, critique, revise.
- Add typed state.
- Add fallback paths and error recovery.

### Layer 4: Summary Chains

File:

```text
src/research_system/chains/summary_chain.py
```

Current prompts:

```python
writer_prompt
critic_prompt
```

Current chain wrappers:

```python
writer_chain
critic_chain
```

Previous design:

```python
writer_chain = writer_prompt | llm | StrOutputParser()
critic_chain = critic_prompt | llm | StrOutputParser()
```

Problem:

- The chain was created immediately at import time.
- The chain depended on a model object that was also created immediately.
- Tests and CI could fail just from importing the module.

Current design:

```python
writer_chain = LazyChain(build_writer_chain)
critic_chain = LazyChain(build_critic_chain)
```

What `LazyChain` does:

```text
import summary_chain
-> create prompts
-> create LazyChain wrappers
-> do not create the actual LLM chain yet

writer_chain.invoke(payload)
-> LazyChain checks if real chain exists
-> if not, build the chain
-> invoke the real chain
```

Why this exists:

- Keeps the public API the same: `writer_chain.invoke(...)`.
- Avoids model initialization during import.
- Makes tests easier to mock.
- Makes CI more reliable.

Current weakness:

- Writer and critic outputs are plain strings.
- There is no structured schema for report sections, citations, or critique score.
- The critic does not automatically trigger a revision loop.

Iteration 2 improvement:

- Use structured output models.
- Make report output citation-aware.
- Add a critic-to-revision loop.
- Add evaluation checks for unsupported claims.

### Layer 5: Pipeline

File:

```text
src/research_system/pipelines/research_pipeline.py
```

Current function:

```python
run_research_pipeline(topic: str) -> dict
```

What it does:

- Creates a state dictionary.
- Calls the search agent.
- Calls the research/scraping agent.
- Calls the writer chain.
- Calls the critic chain.
- Returns the final state.

Why this layer exists:

- It is the current orchestration layer.
- It defines the order of operations.
- It keeps the app entry point simple.

Current weakness:

- Pipeline state is an untyped dictionary.
- Control flow is linear.
- There is no branching, retry, timeout, or fallback path.
- It uses `print()` instead of structured logs/events.
- It is not streaming.

Iteration 2 improvement:

- Replace this linear pipeline with a LangGraph workflow.
- Use a typed state object.
- Add graph nodes and edges.
- Add structured logging and tracing.
- Add streaming output support.

### Current end-to-end flow by file

```text
main.py
-> calls run_research_pipeline(topic)

research_pipeline.py
-> calls build_search_agent()

search_agent.py
-> calls get_llm()
-> gives agent access to web_search

tool.py
-> web_search calls Tavily

research_pipeline.py
-> receives search result
-> calls build_research_agent()

research_agent.py
-> calls get_llm()
-> gives agent access to scrape_url

tool.py
-> scrape_url fetches and extracts page text

research_pipeline.py
-> combines search results and scraped content
-> calls writer_chain.invoke(...)

summary_chain.py
-> LazyChain builds writer chain on first invoke
-> writer prompt + LLM + output parser

research_pipeline.py
-> calls critic_chain.invoke(...)

summary_chain.py
-> LazyChain builds critic chain on first invoke
-> critic prompt + LLM + output parser

research_pipeline.py
-> returns state dictionary
```

### Why this architecture exists

The project is intentionally split into layers:

```text
tools = external actions
models = provider selection
agents = reasoning + tool access
chains = prompt-based transformations
pipeline = orchestration
tests = safety net
CI = remote quality gate
pre-commit = local quality gate
```

Why this matters:

- Each layer has one responsibility.
- Each layer can be tested separately.
- Each layer can be replaced as the project matures.
- The codebase can grow toward a real agentic platform instead of staying a single script.

### What is good in Iteration 1?

- There is a working end-to-end flow.
- Tools are separated from agents.
- Model selection is separated from orchestration.
- OpenAI and Groq provider hooks exist.
- LangGraph agent builder functions exist.
- Chains are lazy and more testable.
- Tests mock external APIs.
- CI, pre-commit, Ruff, mypy, and coverage exist.

### What is missing in Iteration 1?

- No LangGraph orchestration yet.
- No typed pipeline state.
- No structured tool outputs.
- No source ranking.
- No citation validation.
- No caching.
- No retry/fallback policy.
- No streaming.
- No observability/tracing.
- No real UI/API layer.
- No evaluation dataset.

---

## Roadmap: Planned Improvements

Iteration 2 should focus on turning the linear pipeline into a more explicit agentic system.

Recommended focus:

1. Replace linear pipeline with LangGraph.
2. Add typed state.
3. Return structured search/scrape results.
4. Add source ranking.
5. Add retry and timeout policies.
6. Add structured logging.
7. Add a first evaluation dataset.

Proposed graph:

```text
input topic
-> search node
-> rank sources node
-> scrape node
-> write report node
-> critique node
-> revise node
-> final output
```

Why this should be next:

- LangGraph makes the control flow explicit.
- Typed state makes debugging easier.
- Structured outputs make evaluation and citation checking possible.
- Retries and fallbacks move the project closer to production-grade agentic engineering.
