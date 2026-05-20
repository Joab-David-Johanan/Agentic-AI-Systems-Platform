from fastapi import APIRouter

from apps.api.schemas.runs import RunRequest, RunResponse
from apps.api.services.run_service import start_run

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", response_model=RunResponse)
def create_run(request: RunRequest) -> RunResponse:
    return start_run(request)
