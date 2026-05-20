from typing import Any

from langchain.agents.middleware import wrap_model_call


def validate_model_and_tools(model: Any, tools: list[Any]) -> None:
    if model is None:
        raise ValueError("Agent model is not configured.")

    for tool in tools:
        if isinstance(tool, dict):
            tool_name = tool.get("name") or tool.get("function", {}).get("name")
            if not tool_name:
                raise ValueError("Tool dictionary is missing a name.")
            continue

        if not getattr(tool, "name", None):
            raise ValueError("Tool is missing a name.")

        if not getattr(tool, "args_schema", None):
            raise ValueError(f"Tool '{tool.name}' is missing an args_schema.")


@wrap_model_call(name="ValidateModelRequest")
def validate_model_request(request: Any, handler: Any):
    # Model middleware is the last cheap place to catch bad model/tool wiring.
    validate_model_and_tools(request.model, list(request.tools or []))
    return handler(request)
