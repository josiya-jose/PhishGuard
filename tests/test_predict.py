import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_valid_url():
    response = client.post("/predict", json={
        "url": "https://google.com",
        "user_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 0


def test_short_url():
    response = client.post("/predict", json={
        "url": "http://a.co",
        "user_id": 1
    })
    assert response.status_code == 200


def test_invalid_url():
    response = client.post("/predict", json={
        "url": "not-a-url",
        "user_id": 1
    })
    assert response.status_code == 200


def test_missing_url():
    response = client.post("/predict", json={
        "user_id": 1
    })
    assert response.status_code == 422


def test_wrong_type():
    response = client.post("/predict", json={
        "url": 12345,
        "user_id": "abc"
    })
    assert response.status_code == 422


def test_phishing_url():
    response = client.post("/predict", json={
        "url": "http://free-login-secure-update.xyz",
        "user_id": 1
    })
    data = response.json()
    assert data["risk_score"] > 70


def test_aps_formula():
    response = client.post("/predict", json={
        "url": "https://google.com",
        "user_id": 1
    })

    data = response.json()

    R = data["risk_score"] / 100
    confidence = data["confidence"]

    expected = (1 - R) * confidence * 100

    assert abs(data["anti_phishing_score"] - expected) < 1


def test_safe_vs_phishing():
    safe = client.post("/predict", json={
        "url": "https://google.com",
        "user_id": 1
    }).json()

    phishing = client.post("/predict", json={
        "url": "http://free-login-secure-update.xyz",
        "user_id": 1
    }).json()

    assert safe["risk_score"] < phishing["risk_score"]
    assert safe["anti_phishing_score"] > phishing["anti_phishing_score"]


def test_confidence():
    response = client.post("/predict", json={
        "url": "https://google.com",
        "user_id": 1
    })

    data = response.json()

    R = data["risk_score"] / 100
    expected = max(R, 1 - R)

    assert abs(data["confidence"] - expected) < 0.01