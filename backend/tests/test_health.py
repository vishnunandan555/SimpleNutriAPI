from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "SimpleNutri API"
    assert "healthy" in data["database"]

def test_version_endpoint():
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_version"] == "1.0.0"
    assert data["schema_version"] == "1.0"
    assert "ifct" in data["source_versions"]
    assert "counts" in data
    assert data["counts"]["foods"] >= 540
    assert data["counts"]["nutrients"] >= 20
    assert data["counts"]["recipes"] >= 5
    assert data["offline_bundle_available"] is True

def test_sources_endpoint():
    response = client.get("/api/v1/sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 2
    source_ids = [s["id"] for s in sources]
    assert "source-ifct-2017" in source_ids

def test_health_head_method():
    response = client.head("/health")
    assert response.status_code == 200
    assert "x-process-time-ms" in response.headers

def test_security_and_latency_headers():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "x-process-time-ms" in response.headers
    process_time = float(response.headers["x-process-time-ms"])
    assert process_time >= 0.0
