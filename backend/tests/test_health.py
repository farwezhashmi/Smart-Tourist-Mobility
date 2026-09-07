from fastapi.testclient import TestClient

from app.main import app


def test_health_route_is_registered() -> None:
    routes = {route.path for route in app.routes}
    assert "/api/health" in routes


def test_trip_search_returns_seeded_alternatives() -> None:
    client = TestClient(app)
    locations = client.get("/api/locations").json()
    source = next(location for location in locations if location["name"] == "Secunderabad Railway Station")
    destination = next(location for location in locations if location["name"] == "Charminar")

    response = client.post(
        "/api/trips/search",
        json={
            "source_location_id": source["id"],
            "destination_location_id": destination["id"],
            "passengers": 3,
            "preference": "cheapest",
            "max_walking_distance_m": 800,
            "accessibility_required": False,
            "budget_inr": 500,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["alternatives"]) == 4
    assert sum(route["is_recommended"] for route in body["alternatives"]) == 1


def test_trip_search_rejects_same_location() -> None:
    client = TestClient(app)
    locations = client.get("/api/locations").json()
    location_id = locations[0]["id"]

    response = client.post(
        "/api/trips/search",
        json={
            "source_location_id": location_id,
            "destination_location_id": location_id,
            "passengers": 1,
            "preference": "balanced",
            "max_walking_distance_m": 800,
            "accessibility_required": False,
        },
    )

    assert response.status_code == 422
