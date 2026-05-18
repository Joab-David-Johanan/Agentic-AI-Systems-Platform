# Multi-Agent Research System

A flexible multi-agent research framework built on LangChain for automated information gathering, synthesis, and analysis. The system uses specialized agents to search the web, process research documents, and generate comprehensive summaries from multiple sources.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd Multi-Agent-Research-System
```

```bash
# Create a Python environment
conda create -n agent-env python=3.10
conda activate agent-env
```

```bash
# Install the package in development mode
pip install -e .
```

If any runtime requirements are missing after the editable install, install the listed dependencies as needed:

```bash
pip install -r requirements.txt
```

Create a `.env` file with required credentials:

```bash
echo "OPENAI_API_KEY=your_key_here" > .env
echo "TAVILY_API_KEY=your_key_here" >> .env
```

The repository includes a Streamlit UI file at `ui/app.py`, but the UI is not yet ready for production use.

### Example Usage

```python
from research_system.pipelines.research_pipeline import run_research_pipeline

result = run_research_pipeline(topic="What are recent developments in quantum computing?")
print(result)
```

### Custom Agent Example

```python
from research_system.agents.search_agent import build_search_agent

search_agent = build_search_agent()
results = search_agent.invoke({
    "messages": [
        (
            "user",
            "Find recent, reliable, and detailed information about: machine learning trends 2024",
        )
    ]
})
print(results)
```

## Architecture

The system follows a modular agent-based architecture where each component has a specific responsibility:

### Core Components

1. **Agents** - Specialized autonomous units that perform specific tasks
   - Search Agent: Queries external sources via Tavily API and web scraping
   - Research Agent: Processes and analyzes research documents
   - Coordinator: Orchestrates multi-step research workflows

2. **Chains** - LangChain expressions that combine LLM operations
   - Summary Chain: Generates concise summaries from research data
   - Analysis Chain: Performs deeper content analysis and synthesis

3. **Pipelines** - End-to-end workflows combining agents and chains
   - Research Pipeline: Orchestrates the complete research process

4. **Tools** - Pluggable utilities for specific operations
   - Web Search: Tavily API integration for real-time search
   - Document Processing: BeautifulSoup and Trafilatura for content extraction

5. **Models** - LLM configuration and selection logic
   - Support for OpenAI models and extensible provider architecture

### Data Flow

```
User Query
    |
    v
Search Agent --> Web/API sources
    |
    v
Document Processing --> Extracted content
    |
    v
Analysis & Summarization --> Research Agent
    |
    v
Output --> UI / API
```

## Project Structure

```
.
├── src/research_system/           # Main package
│   ├── agents/                    # Agent implementations
│   │   ├── research_agent.py      # Document analysis agent
│   │   └── search_agent.py        # Web search agent
│   ├── chains/                    # LangChain chain definitions
│   │   └── summary_chain.py       # Summarization pipeline
│   ├── config/                    # Configuration management
│   ├── models/                    # LLM model selection
│   │   └── model_selection.py     # Model initialization
│   ├── pipelines/                 # Complete workflows
│   │   └── research_pipeline.py   # Main research orchestration
│   ├── tools/                     # Utility tools
│   │   └── tool.py                # Tool definitions
│   └── utils/                     # Helper functions
│       └── logger.py              # Logging configuration
├── ui/                            # Streamlit web interface
│   └── app.py                     # Main UI application
├── tests/                         # Test suite
├── assets/                        # Documentation and notes
│   ├── progress.md                # Development progress
│   └── learnings.md               # Technical learnings
├── pyproject.toml                 # Project configuration and dependencies
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

### Requirements

- Python 3.10 or higher
- pip or conda package manager
- API keys for OpenAI and Tavily (optional, for full functionality)

### Setup Steps

1. Clone and navigate to the project:
   ```bash
   git clone <repository-url>
   cd Multi-Agent-Research-System
   ```

2. Create a virtual environment:
   ```bash
   conda create -n agent-env python=3.10
   conda activate agent-env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

5. Configure environment variables:
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_key_here" > .env
   echo "TAVILY_API_KEY=your_key_here" >> .env
   ```

## Usage

### Running the Web UI

```bash
streamlit run ui/app.py
```

This launches a web interface where you can input research queries and interact with the system.

### Using the Research Pipeline Programmatically

```python
from research_system.pipelines.research_pipeline import ResearchPipeline

pipeline = ResearchPipeline()
result = pipeline.run(query="What are recent developments in quantum computing?")
print(result)
```

### Custom Agent Usage

```python
from research_system.agents.search_agent import SearchAgent

search_agent = SearchAgent()
results = search_agent.search("machine learning trends 2024")
```

## Dependencies

### Core Framework

- **langchain** (>=0.2.0) - LLM orchestration and chain management
- **langchain-core** (>=0.2.0) - Core LangChain abstractions
- **langchain-community** (>=0.2.0) - Community integrations
- **langchain-openai** (>=0.1.0) - OpenAI model support

### Search and Web Tools

- **tavily-python** (>=0.3.0) - Real-time web search API
- **beautifulsoup4** (>=4.12.0) - HTML parsing
- **trafilatura** - Content extraction from web pages
- **requests** (>=2.31.0) - HTTP library
- **lxml** (>=5.0.0) - XML/HTML processing

### Interface and Utilities

- **streamlit** (>=1.0.0) - Web UI framework
- **python-dotenv** (>=1.0.0) - Environment variable management
- **rich** (>=13.7.0) - Terminal output formatting

### Development Requirements

- **pytest** - Testing framework (recommended)
- **black** - Code formatting (recommended)
- **mypy** - Type checking (recommended)

## Roadmap

### Phase 1: Foundation (Current)

- [x] Core agent architecture
- [x] Web search integration
- [x] Document processing pipeline
- [x] Summary generation
- [x] Streamlit UI

### Phase 2: Enhanced Capabilities

- [ ] **Caching Layer**: Implement Redis-based caching for search results and processed documents to reduce API calls and improve response times
- [ ] **Evaluation Pipeline**: Build metrics and benchmarks for evaluating research quality, accuracy, and relevance of generated summaries
- [ ] **Multi-Source Integration**: Add support for academic databases, news feeds, and domain-specific APIs
- [ ] **Persistent Storage**: Database integration for storing research history and results

### Phase 3: Production Readiness

- [ ] **Guardrails System**: Implement content validation, fact-checking integration, and quality thresholds for outputs
- [ ] **Observability Dashboard**: Real-time monitoring of agent performance, latency metrics, and API usage
- [ ] **Structured Logging**: Enhanced logging with structured output for debugging and analytics
- [ ] **Error Recovery**: Resilient agent workflows with retry logic and fallback strategies

### Phase 4: Advanced Features

- [ ] **Fine-tuning Pipeline**: Support for training custom models on domain-specific research data
- [ ] **Collaborative Research**: Multi-user support with shared research projects
- [ ] **Export Formats**: Generate reports in multiple formats (PDF, Markdown, JSON)
- [ ] **Vector Search**: Semantic search across research repositories using embeddings

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes with clear messages
4. Push to your fork and submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.