from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

WorkflowStatus = Literal["pending", "running", "completed", "warning", "failed", "skipped"]


class WorkflowEvent(BaseModel):
    run_id: str
    node: str
    status: WorkflowStatus
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
