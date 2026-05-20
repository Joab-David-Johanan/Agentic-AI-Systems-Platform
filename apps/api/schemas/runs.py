from typing import Literal

from pydantic import BaseModel, Field

RuntimeChoice = Literal["langchain", "langgraph"]
ProviderChoice = Literal["openai", "groq"]


class RunRequest(BaseModel):
    question: str = Field(..., min_length=1)
    runtime: RuntimeChoice = "langchain"
    provider: ProviderChoice = "openai"


class RunResponse(BaseModel):
    run_id: str
    status: str
    runtime: RuntimeChoice
    provider: ProviderChoice
