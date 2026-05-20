import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_openai_llm():
    """Create the OpenAI chat model lazily so imports do not require API credentials."""
    from langchain_openai import ChatOpenAI

    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    return ChatOpenAI(model=model_name, temperature=0)


@lru_cache(maxsize=1)
def get_groq_llm():
    """Create the Groq chat model lazily so imports do not require API credentials."""
    from langchain_groq import ChatGroq

    model_name = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")
    return ChatGroq(model=model_name, temperature=0)


def get_llm(provider: str | None = None):
    """Return the configured chat model provider."""
    selected_provider = provider or os.getenv("LLM_PROVIDER") or "openai"
    selected_provider = selected_provider.lower()

    if selected_provider == "groq":
        return get_groq_llm()

    if selected_provider == "openai":
        return get_openai_llm()

    raise ValueError(f"Unsupported LLM provider: {selected_provider}")
