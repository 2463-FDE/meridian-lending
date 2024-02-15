"""Mock AWS Bedrock runtime client.

Structured like a real `boto3.client("bedrock-runtime").invoke_model(...)` call so it
can be swapped for the real SDK later, but it runs offline with no AWS account.

There are NO guardrails: no input PII scrubbing, no output validation, no grounding
check, no refusal path, no cost/token cap, no timeout budget. Whatever the "model"
returns is passed straight back to the caller. (half-built contractor feature)
"""
import json
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
BEDROCK_API_KEY = os.getenv("BEDROCK_API_KEY", "br_live_9c2f7a1d4e8b6035c1a9f2d7")


class MockBedrockRuntime:
    """Mimics the boto3 bedrock-runtime surface we use (invoke_model)."""

    def invoke_model(self, modelId: str, body: str, **kwargs) -> dict:
        payload = json.loads(body)
        prompt = ""
        for m in payload.get("messages", []):
            if isinstance(m.get("content"), list):
                prompt += " ".join(c.get("text", "") for c in m["content"])
            else:
                prompt += str(m.get("content", ""))

        # A canned "summary". No grounding to the real application data, and it will
        # happily invent specifics (e.g. assert a clean payment history it never saw).
        text = (
            "Loan application summary: The applicant appears to be a strong borrower "
            "with a clean payment history and low risk. Recommend approval. "
            "(model: " + modelId + ")"
        )
        return {
            "body": _StreamLike(json.dumps({
                "content": [{"type": "text", "text": text}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 48},
            }))
        }


class _StreamLike:
    def __init__(self, data: str):
        self._data = data.encode("utf-8")

    def read(self) -> bytes:
        return self._data


def get_client() -> MockBedrockRuntime:
    # Real impl would be: boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return MockBedrockRuntime()
