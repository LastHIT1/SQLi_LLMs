import os
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Final

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from openai import AsyncOpenAI
from redis.asyncio import ConnectionPool, Redis

EXCLUDE_PATHS: Final[frozenset[str]] = frozenset()
STATIC_PREFIX: Final[str] = "/static/"

ALLOWED_RESPONSE: Final[Response] = Response(
    content=b'{"allowed":true}',
    media_type="application/json",
)

SQLI_PROMPT: Final[str] = """Detect SQL injection in the input. Analyze for:
- SQL keywords (SELECT, UNION, DROP, INSERT, UPDATE, DELETE)
- Comments (--, /*, #)
- Quote manipulation (' or ")
- Boolean injection (OR 1=1, AND 1=1)
- Time-based (SLEEP, WAITFOR)

Reply exactly:
DETECTED: true/false
THREAT: [type or "none"]
PAYLOAD: [payload or "none"]"""

DETECTED_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"DETECTED:\s*(true|false)", re.IGNORECASE
)
THREAT_PATTERN: Final[re.Pattern[str]] = re.compile(r"THREAT:\s*(.+)", re.IGNORECASE)
PAYLOAD_PATTERN: Final[re.Pattern[str]] = re.compile(r"PAYLOAD:\s*(.+)", re.IGNORECASE)

redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None
openai_client: AsyncOpenAI | None = None


@lru_cache(maxsize=1)
def get_openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_pool, redis_client, openai_client
    redis_pool = ConnectionPool(host="cache", port=6379, db=0, decode_responses=True)
    redis_client = Redis(connection_pool=redis_pool)
    openai_client = AsyncOpenAI(api_key=get_openai_api_key())
    yield
    await redis_client.aclose()
    await redis_pool.disconnect()


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)


async def get_guardrail_status() -> bool:
    value = await redis_client.get("guardrail_status")
    if value is None:
        await redis_client.set("guardrail_status", "1")
        return True
    return value == "1"


def parse_llm_response(output: str) -> tuple[bool, str, str]:
    detected = False
    threat_type = "SQL Injection Attempt"
    payload = "Not identified"

    if match := DETECTED_PATTERN.search(output):
        detected = match.group(1).lower() == "true"

    if match := THREAT_PATTERN.search(output):
        value = match.group(1).strip()
        if value.lower() != "none":
            threat_type = value

    if match := PAYLOAD_PATTERN.search(output):
        value = match.group(1).strip()
        if value.lower() != "none":
            payload = value

    return detected, threat_type, payload


@app.post("/", response_model=None)
async def check_request(request: Request) -> Response:
    if not await get_guardrail_status():
        return ALLOWED_RESPONSE

    url = request.headers.get("X-Original-URI", "")

    if url.startswith(STATIC_PREFIX):
        return ALLOWED_RESPONSE

    method = request.headers.get("X-Original-Method", "GET")

    if method == "GET" and url in EXCLUDE_PATHS:
        return ALLOWED_RESPONSE

    body = await request.body()
    body_str = body.decode("utf-8", errors="replace") if body else ""

    response = await openai_client.responses.create(
        model="gpt-4.1-nano",
        instructions=SQLI_PROMPT,
        input=f"URL: {url}\nBody: {body_str}",
    )

    detected, threat_type, payload = parse_llm_response(response.output_text)

    if not detected:
        return ALLOWED_RESPONSE

    return JSONResponse(
        status_code=403,
        content={
            "blocked": True,
            "threat_type": threat_type,
            "payload": payload,
            "target_url": url,
            "method": method,
        },
    )


@app.get("/status")
async def status() -> dict[str, bool]:
    return {"active": await get_guardrail_status()}


@app.get("/activate")
async def activate() -> dict[str, str]:
    await redis_client.set("guardrail_status", "1")
    return {"status": "activated"}


@app.get("/deactivate")
async def deactivate() -> dict[str, str]:
    await redis_client.set("guardrail_status", "0")
    return {"status": "deactivated"}
