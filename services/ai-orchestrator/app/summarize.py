"""Loan-application summary assistant.

Builds a Bedrock invoke_model call and returns the raw model text to the caller with
NO output validation, NO grounding check, NO refuse-if-unknown. The full application
record (including PII) is put straight into the prompt. (no guardrails)
"""
import json
from .bedrock_client import get_client, BEDROCK_MODEL_ID


def summarize_application(application: dict) -> dict:
    client = get_client()
    # entire record (name, ssn, income, ...) goes into the prompt unredacted
    prompt = (
        "Summarize this loan application for a loan officer:\n"
        + json.dumps(application)
    )
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    })
    resp = client.invoke_model(modelId=BEDROCK_MODEL_ID, body=body)
    raw = json.loads(resp["body"].read())
    text = raw["content"][0]["text"]
    # returned directly — no validation, no grounding, no refusal
    return {"summary": text, "usage": raw.get("usage", {})}
