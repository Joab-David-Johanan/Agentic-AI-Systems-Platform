from research_system.middleware.model_validation import validate_model_request
from research_system.middleware.prompt_validation import validate_prompt_before_model
from research_system.middleware.tool_validation import validate_and_handle_tool_call

DEFAULT_AGENT_MIDDLEWARE = [
    validate_prompt_before_model,
    validate_model_request,
    validate_and_handle_tool_call,
]

__all__ = [
    "DEFAULT_AGENT_MIDDLEWARE",
    "validate_and_handle_tool_call",
    "validate_model_request",
    "validate_prompt_before_model",
]
