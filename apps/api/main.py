from fastapi import FastAPI

from apps.api.routes.runs import router as runs_router

app = FastAPI(title="Agentic AI Systems Platform API")
app.include_router(runs_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
