from fastapi.testclient import TestClient
import app.main as main

def test_health_endpoint():
    client = TestClient(main.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_countries_endpoint():
    response = TestClient(main.app).get("/countries")
    assert response.status_code == 200
    assert "India" in response.json()["countries"]

def test_invalid_country_returns_400(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("Unknown country")
    monkeypatch.setattr(main, "forecast_country", fail)
    response = TestClient(main.app).get("/predict?country=Atlantis&months=2")
    assert response.status_code == 400

def test_month_validation():
    response = TestClient(main.app).get("/predict?months=20")
    assert response.status_code == 422

def test_monitoring_endpoint():
    response = TestClient(main.app).get("/monitoring")
    assert response.status_code == 200
    assert "requests_total" in response.json()


def test_country_prediction_endpoint(monkeypatch):
    def fake_forecast(country, months=3):
        return [{"country": country, "date": "2025-01-01", "predicted_sales": 123.4}]
    monkeypatch.setattr(main, "forecast_country", fake_forecast)
    response = TestClient(main.app).get("/predict?country=India&months=1")
    assert response.status_code == 200
    assert response.json()["country"] == "India"
    assert response.json()["predictions"][0]["predicted_sales"] == 123.4

def test_all_countries_prediction_endpoint(monkeypatch):
    def fake_forecast_all(months=3):
        return [{"country": "ALL", "date": "2025-01-01", "predicted_sales": 500.0}]
    monkeypatch.setattr(main, "forecast_all", fake_forecast_all)
    response = TestClient(main.app).get("/predict?months=1")
    assert response.status_code == 200
    assert response.json()["country"] == "ALL"
    assert response.json()["predictions"][0]["predicted_sales"] == 500.0
