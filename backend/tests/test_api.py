from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_loads(client):
    response = client.get("/api/loads")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_battery(client):
    response = client.get("/api/battery")
    assert response.status_code == 200
    assert "capacity_kwh" in response.json()

def test_get_forecast(client):
    response = client.get("/api/forecast")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
