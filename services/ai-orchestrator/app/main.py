"""AI orchestrator — FastAPI. Half-built loan-summary assistant on (mock) Bedrock."""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from . import summarize

app = FastAPI(title="Meridian AI Orchestrator", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai-orchestrator"}


class SummaryIn(BaseModel):
    app_id: Optional[int] = None
    name: Optional[str] = None
    ssn: Optional[str] = None
    income: Optional[float] = None
    amount: Optional[float] = None
    purpose: Optional[str] = None


@app.post("/summarize")
def summarize_app(body: SummaryIn):
    # no input scrubbing; whole body forwarded to the model
    return summarize.summarize_application(body.model_dump())
