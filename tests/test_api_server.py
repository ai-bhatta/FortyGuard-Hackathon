from fastapi.testclient import TestClient

from api_server import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_assets_endpoint_returns_demo_assets():
    response = client.get("/assets")

    assert response.status_code == 200
    assert len(response.json()) == 12


def test_risks_endpoint_returns_ranked_payload():
    response = client.get("/risks")
    payload = response.json()

    assert response.status_code == 200
    assert payload[0]["risk_score"] >= payload[-1]["risk_score"]
    assert {"asset_id", "risk_score", "risk_level", "factors"} <= set(payload[0])


def test_risks_endpoint_filters_by_level():
    response = client.get("/risks", params={"risk_level": "Low"})

    assert response.status_code == 200
    assert {item["risk_level"] for item in response.json()} == {"Low"}


def test_single_asset_risk_endpoint():
    response = client.get("/risks/A001")

    assert response.status_code == 200
    assert response.json()["asset_id"] == "A001"


def test_missing_asset_returns_404():
    response = client.get("/risks/NOPE")

    assert response.status_code == 404
