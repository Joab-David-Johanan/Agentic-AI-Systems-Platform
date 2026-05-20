from uuid import uuid4

from apps.api.schemas.runs import RunRequest, RunResponse


def start_run(request: RunRequest) -> RunResponse:
    run_id = f"run_{uuid4().hex[:12]}"
    return RunResponse(
        run_id=run_id,
        status="created",
        runtime=request.runtime,
        provider=request.provider,
    )
