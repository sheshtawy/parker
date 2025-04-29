from fastapi.testclient import TestClient
import pytest
from server import app

client = TestClient(app)

def test_search_endpoint_valid_request():
    response = client.post("/", json=[
        {"length": 20, "quantity": 2},
        {"length": 30, "quantity": 1}
    ])
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    for result in results:
        assert "location_id" in result
        assert "listing_ids" in result
        assert "total_price_in_cents" in result

def test_search_endpoint_invalid_vehicle_count():
    response = client.post("/", json=[
        {"length": 20, "quantity": 3},
        {"length": 30, "quantity": 3}  # Total vehicles > 5
    ])
    assert response.status_code == 422  # Validation error
    assert response.json()["detail"][0]["msg"] == "Value error, Total number of vehicles cannot exceed 5"

def test_search_endpoint_invalid_input():
    # Missing required fields
    response = client.post("/", json=[
        {"length": 20}  # Missing quantity
    ])
    assert response.status_code == 422

    # Invalid value types
    response = client.post("/", json=[
        {"length": "invalid", "quantity": 1}  # length should be integer
    ])
    assert response.status_code == 422

def test_search_endpoint_empty_request():
    response = client.post("/", json=[])
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, At least one vehicle entry is required"