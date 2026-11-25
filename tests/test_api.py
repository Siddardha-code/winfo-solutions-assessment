from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.llm import MockTriageService, TriageError
from app.main import app, get_service

client = TestClient(app)
TICKET = {"subject": "Charged twice", "body": "I was charged twice for my invoice this month."}


def setup_function():
    app.dependency_overrides.clear()
    app.dependency_overrides[get_service] = lambda: MockTriageService()
    app.dependency_overrides[get_settings] = lambda: Settings("us-east-1", "test-model", "mock", None, 100)


def test_health():
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").status_code == 200


def test_analyse_ok():
    r = client.post("/v1/tickets/analyse", json=TICKET)
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "billing"
    assert body["priority"] in {"low", "medium", "high", "urgent"}
    assert body["request_id"] and body["model_id"] == "test-model"


def test_validation_rejects_empty_body():
    assert client.post("/v1/tickets/analyse", json={"subject": "x", "body": ""}).status_code == 422


def test_api_key_enforced():
    app.dependency_overrides[get_settings] = lambda: Settings("us-east-1", "m", "mock", "secret", 100)
    assert client.post("/v1/tickets/analyse", json=TICKET).status_code == 401
    ok = client.post("/v1/tickets/analyse", json=TICKET, headers={"x-api-key": "secret"})
    assert ok.status_code == 200


def test_llm_failure_maps_to_502():
    class Broken:
        def analyse(self, _):
            raise TriageError("boom", 502)

    app.dependency_overrides[get_service] = lambda: Broken()
    assert client.post("/v1/tickets/analyse", json=TICKET).status_code == 502
