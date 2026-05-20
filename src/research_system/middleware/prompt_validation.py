from typing import Any

from langchain.agents.middleware import AgentState, Runtime, before_model

MAX_PROMPT_CHARS = 12_000
MAX_REPEATED_CHAR_RUN = 80
MAX_WORD_REPEAT_RATIO = 0.45

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "disregard all previous instructions",
    "forget previous instructions",
    "forget all previous instructions",
    "reveal your system prompt",
    "show me your system prompt",
    "print your system prompt",
    "developer message",
    "system message",
    "bypass safety",
    "jailbreak",
    "act as dan",
]

TOOL_OVERRIDE_PATTERNS = [
    "disable tools",
    "skip tool validation",
    "do not call tools",
    "call this tool instead",
    "override tool",
    "fake tool result",
    "return a fabricated source",
    "invent sources",
]


def extract_message_text(message: Any) -> str:
    """Pull readable text from the message shapes LangChain commonly uses."""
    content = getattr(message, "content", None)

    if content is None and isinstance(message, dict):
        content = message.get("content")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return " ".join(str(part) for part in content)

    return str(content or "")


def validate_prompt_messages(messages: list[Any]) -> None:
    if not messages:
        raise ValueError("Agent state must include at least one message before model execution.")

    prompt_text = "\n".join(extract_message_text(message) for message in messages).strip()
    normalized_prompt = " ".join(prompt_text.lower().split())

    if not prompt_text:
        raise ValueError("Agent prompt is empty after message extraction.")

    if len(prompt_text) > MAX_PROMPT_CHARS:
        raise ValueError(
            f"Agent prompt is too large for this workflow: {len(prompt_text)} characters."
        )

    if contains_prompt_injection(normalized_prompt):
        raise ValueError("Agent prompt contains prompt-injection style instructions.")

    if contains_tool_override_attempt(normalized_prompt):
        raise ValueError("Agent prompt attempts to override tool or source-handling rules.")

    if looks_like_spam(prompt_text):
        raise ValueError("Agent prompt looks like spam or low-quality repeated text.")


def contains_prompt_injection(prompt_text: str) -> bool:
    return any(pattern in prompt_text for pattern in PROMPT_INJECTION_PATTERNS)


def contains_tool_override_attempt(prompt_text: str) -> bool:
    return any(pattern in prompt_text for pattern in TOOL_OVERRIDE_PATTERNS)


def looks_like_spam(prompt_text: str) -> bool:
    if has_long_repeated_character_run(prompt_text):
        return True

    words = [word.strip(".,!?;:()[]{}\"'").lower() for word in prompt_text.split()]
    words = [word for word in words if word]

    if len(words) < 12:
        return False

    most_common_count = max(words.count(word) for word in set(words))
    return most_common_count / len(words) > MAX_WORD_REPEAT_RATIO


def has_long_repeated_character_run(prompt_text: str) -> bool:
    current_char = ""
    current_run = 0

    for char in prompt_text:
        if char == current_char:
            current_run += 1
        else:
            current_char = char
            current_run = 1

        if current_run >= MAX_REPEATED_CHAR_RUN:
            return True

    return False


@before_model(name="ValidatePromptBeforeModel")
def validate_prompt_before_model(state: AgentState, runtime: Runtime) -> None:
    # Keep this middleware small: it protects the model boundary before tokens are spent.
    messages = state.get("messages", [])
    validate_prompt_messages(list(messages))
