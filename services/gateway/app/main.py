"""API gateway / BFF — FastAPI.

Routes the Next.js portal to the LOS, LSS, and AI services. Auth is a thin bearer-token
pass-through; the gateway does not enforce roles (downstream services don't either).
"""
import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

ORIGINATION_URL = os.getenv("ORIGINATION_URL", "http://origination-service:8001")
SERVICING_URL = os.getenv("SERVICING_URL", "http://servicing-service:8002")
AI_URL = os.getenv("AI_ORCHESTRATOR_URL", "http://ai-orchestrator:8003")

app = FastAPI(title="Meridian Gateway (BFF)", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


async def _proxy(base: str, path: str, request: Request):
    method = request.method
    body = await request.body()
    async with httpx.AsyncClient(timeout=35) as client:
        resp = await client.request(
            method, f"{base}{path}",
            content=body,
            headers={k: v for k, v in request.headers.items()
                     if k.lower() not in ("host", "content-length")},
            params=request.query_params,
        )
    try:
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except Exception:
        return JSONResponse(status_code=resp.status_code, content={"raw": resp.text})


@app.api_route("/los/{path:path}", methods=["GET", "POST"])
async def los(path: str, request: Request):
    return await _proxy(ORIGINATION_URL, f"/{path}", request)


@app.api_route("/lss/{path:path}", methods=["GET", "POST"])
async def lss(path: str, request: Request):
    return await _proxy(SERVICING_URL, f"/{path}", request)


@app.api_route("/ai/{path:path}", methods=["GET", "POST"])
async def ai(path: str, request: Request):
    return await _proxy(AI_URL, f"/{path}", request)
