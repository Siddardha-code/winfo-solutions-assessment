import json
import logging
import secrets
import sys
import uuid
from functools import lru_cache

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import Settings, get_settings
from app.llm import BedrockTriageService, MockTriageService, TriageError
from app.schemas import TicketIn, TicketOut


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {"level": record.levelname, "logger": record.name, "msg": record.getMessage()}
        for k in ("request_id", "error_code", "path", "status", "category", "priority"):
            if hasattr(record, k):
                data[k] = getattr(record, k)
        return json.dumps(data)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
log = logging.getLogger("api")

app = FastAPI(title="Support Ticket Assistant", version="1.0.0")
Instrumentator(excluded_handlers=["/healthz", "/readyz", "/metrics"]).instrument(app).expose(
    app, include_in_schema=False
)


@lru_cache
def get_service():
    s = get_settings()
    return MockTriageService() if s.llm_mode == "mock" else BedrockTriageService(s)


def require_api_key(x_api_key: str | None = Header(default=None), settings: Settings = Depends(get_settings)):
    if settings.api_key and not (x_api_key and secrets.compare_digest(x_api_key, settings.api_key)):
        raise HTTPException(status_code=401, detail="invalid or missing API key")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["x-request-id"] = rid
    return response


@app.exception_handler(TriageError)
async def triage_error_handler(request: Request, exc: TriageError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.get("/healthz")
def healthz():
    """Liveness: process is up. No downstream calls."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness: app is configured. Deliberately does NOT call Bedrock (avoids cost and cascading failures)."""
    s = get_settings()
    return {"status": "ready", "llm_mode": s.llm_mode, "model_id": s.model_id}


@app.post("/v1/tickets/analyse", response_model=TicketOut, dependencies=[Depends(require_api_key)])
def analyse_ticket(
    ticket: TicketIn,
    request: Request,
    service=Depends(get_service),
    settings: Settings = Depends(get_settings),
):
    # Sync handler on purpose: boto3 is blocking, FastAPI runs this in its threadpool.
    triage = service.analyse(ticket)
    rid = request.state.request_id
    # Log metadata only: never the ticket body (PII).
    log.info(
        "ticket_analysed",
        extra={"request_id": rid, "category": triage.category.value, "priority": triage.priority.value},
    )
    return TicketOut(**triage.model_dump(), request_id=rid, model_id=settings.model_id)
