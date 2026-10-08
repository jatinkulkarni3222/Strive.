"""FastAPI Endpoints Integration Tests."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "squat" in data["supported_sports"]
    assert "Not a medical diagnosis" in data["disclaimer"]


def test_analyze_unsupported_sport():
    files = {"video": ("test.mp4", b"dummy video content", "video/mp4")}
    data = {"sport": "cricket_bowling"}
    response = client.post("/analyze", files=files, data=data)
    assert response.status_code == 400
    assert "Unsupported sport" in response.json()["detail"]


def test_analyze_invalid_file_extension():
    files = {"video": ("test.pdf", b"dummy pdf content", "application/pdf")}
    data = {"sport": "squat"}
    response = client.post("/analyze", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]
