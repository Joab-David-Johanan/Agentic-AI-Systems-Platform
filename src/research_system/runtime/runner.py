from collections.abc import Iterator

from research_system.runtime.events import WorkflowEvent


def run_workflow_with_events(run_id: str, question: str) -> Iterator[WorkflowEvent]:
    yield WorkflowEvent(
        run_id=run_id,
        node="query_received",
        status="completed",
        message=f"Received question: {question}",
    )
    yield WorkflowEvent(
        run_id=run_id,
        node="prompt_validation",
        status="running",
        message="Checking prompt safety and input quality.",
    )
