import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

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
    body = resp.get_json()
    assert "error" in body

def test_ingest_and_query(client):
    payload = {
        "agent_id":     "agent-007",
        "session_id":   "sess-1234",
        "user_id":      "user-4321",
        "timestamp":    "2025-05-16T12:00:00Z",
        "messages": [
            {
                "sequence": 1,
                "sender":   "user",
                "text":     "Hello!",
                "time":     "2025-05-16T12:00:01Z"
            }
        ],
        "metadata": {
            "agent_version":  "1.0.0",
            "policy_version": "2025-05",
            "os":             "Windows 10",
            "application":    "CATDAMS Sentinel",
            "ip_address":     "127.0.0.2",
            "language":       "en-US"
        }
    }

    resp = client.post("/ingest", json=payload)
    assert resp.status_code == 202
    assert resp.get_json() == {"status": "accepted"}

    resp = client.get("/query")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list) and len(data) == 1
    record = data[0]
    assert "timestamp" in record and "data" in record
    assert record["data"] == payload
