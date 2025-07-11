import pytest
from app import db, Telemetry  # optional if you need to inspect models
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.data == b"OK"

def test_query_empty(client):
    resp = client.get("/query")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_ingest_invalid(client):
    resp = client.post("/ingest", json={"foo": "bar"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_ingest_and_query(client):
    payload = {
        "agent_id":     "agent-007",
        "session_id":   "sess-1234",
        "user_id":      "user-4321",
        "timestamp":    "2025-05-16T12:00:00Z",
        "messages": [
            {"sequence":1, "sender":"user", "text":"Hello!", "time":"2025-05-16T12:00:01Z"}
        ],
        "metadata": {
            "agent_version":"1.0.0", "policy_version":"2025-05",
            "os":"Win10", "application":"CATDAMS", "ip_address":"127.0.0.1", "language":"en-US"
        }
    }

    # Ingest
    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 202
    assert resp.get_json() == {"status": "accepted"}

    # Query
    resp = client.get("/query")
    data = resp.get_json()
    assert isinstance(data, list) and len(data) == 1
    assert data[0]["data"] == payload

def test_analytics_health():
    resp = client.get("/api/analytics/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "api_version" in data

def test_analytics_session_summary():
    resp = client.get("/api/analytics/sessions/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_analysis" in data
    assert "threat_analysis" in data
    assert "api_version" in data

def test_analytics_tdc_performance():
    resp = client.get("/api/analytics/tdc/performance")
    assert resp.status_code == 200
    data = resp.json()
    assert "aipc_module" in data
    assert "threat_detection" in data
    assert "api_version" in data
