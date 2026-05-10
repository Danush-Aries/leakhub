from fastapi.testclient import TestClient
from app.api.main import app
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

client = TestClient(app)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
