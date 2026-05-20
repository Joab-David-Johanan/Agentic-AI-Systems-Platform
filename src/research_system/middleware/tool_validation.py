from typing import Any

from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage


def validate_tool_arguments(tool: Any, args: dict[str, Any]) -> None:
    if tool is None:
        raise ValueError("Tool call does not resolve to a registered tool.")

    if not isinstance(args, dict):
        raise ValueError("Tool call arguments must be a dictionary.")

    schema = getattr(tool, "args_schema", None)
    if schema is None:
        return

    if hasattr(schema, "model_validate"):
        schema.model_validate(args)
        return

    if hasattr(schema, "parse_obj"):
        schema.parse_obj(args)


@wrap_tool_call(name="ValidateAndHandleToolCall")
def validate_and_handle_tool_call(request: Any, handler: Any):
    # Tool failures should come back as tool messages, not crash the whole agent run.
    tool_call = request.tool_call
    tool_call_id = tool_call.get("id", "unknown-tool-call")
    tool_args = tool_call.get("args", {})

    try:
        validate_tool_arguments(request.tool, tool_args)
        return handler(request)
    except Exception as exc:
        tool_name = getattr(request.tool, "name", tool_call.get("name", "unknown tool"))
        return ToolMessage(
            content=f"Tool '{tool_name}' failed validation or execution: {exc}",
            tool_call_id=tool_call_id,
        )
