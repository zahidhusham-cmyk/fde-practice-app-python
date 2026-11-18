from fastapi.testclient import TestClient


def test_lists_shipments_with_pagination_metadata(client: TestClient) -> None:
    response = client.get("/api/shipments")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["shipments"], list)
    assert len(body["shipments"]) > 0
    assert body["pagination"] == {
        "page": 1,
        "limit": 10,
        "total": 28,
        "total_pages": 3,
    }


def test_honors_a_custom_page_size(client: TestClient) -> None:
    response = client.get("/api/shipments?limit=5")

    assert response.status_code == 200
    body = response.json()
    assert len(body["shipments"]) == 5
    assert body["pagination"]["limit"] == 5
    assert body["pagination"]["total"] == 28
    assert body["pagination"]["total_pages"] == 6


def test_page_1_includes_the_earliest_shipments_in_default_order(client: TestClient) -> None:
    response = client.get("/api/shipments?page=1&limit=10")

    assert response.status_code == 200
    body = response.json()
    assert len(body["shipments"]) == 10
    assert body["shipments"][0]["id"] == "HL-4401"
    assert body["shipments"][9]["id"] == "HL-4410"
    assert body["pagination"]["total"] == 28


def test_returns_a_shipment_by_id(client: TestClient) -> None:
    response = client.get("/api/shipments/HL-4412")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "HL-4412"
    assert body["customer"] == "Brightleaf Market"
    assert body["status"] == "out_for_delivery"
    assert body["driver_id"] == "drv-maya"
    assert body["origin_city"] == "Baltimore"
    assert body["destination_city"] == "Philadelphia"
    assert len(body["events"]) >= 1


def test_returns_404_for_an_unknown_shipment(client: TestClient) -> None:
    response = client.get("/api/shipments/HL-9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Shipment not found"


def test_updates_shipment_status_along_a_valid_transition(client: TestClient) -> None:
    original = client.get("/api/shipments/HL-4401")
    response = client.patch("/api/shipments/HL-4401", json={"status": "at_origin"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "HL-4401"
    assert body["status"] == "at_origin"
    assert body["updated_at"] != original.json()["updated_at"]


def test_assigns_a_driver(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4401", json={"driver_id": "drv-carter"})

    assert response.status_code == 200
    assert response.json()["driver_id"] == "drv-carter"


def test_rejects_an_invalid_status(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4401", json={"status": "done"})

    assert response.status_code == 422


def test_rejects_an_unknown_driver(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4401", json={"driver_id": "drv-nobody"})

    assert response.status_code == 400
    assert "driver_id" in response.json()["detail"]


def test_rejects_a_patch_with_no_fields(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4401", json={})

    assert response.status_code == 400
    assert "at least one" in response.json()["detail"]


def test_returns_404_when_updating_an_unknown_shipment(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-9999", json={"status": "cancelled"})

    assert response.status_code == 404


def test_rejects_an_illegal_status_transition(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4401", json={"status": "delivered"})

    assert response.status_code == 400
    assert "Cannot transition from booked to delivered" in response.json()["detail"]


def test_delivered_shipments_are_terminal(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4406", json={"status": "in_transit"})

    assert response.status_code == 400
    assert "Cannot transition from delivered to in_transit" in response.json()["detail"]


def test_delayed_shipment_can_return_to_in_transit(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4407", json={"status": "in_transit"})

    assert response.status_code == 200
    assert response.json()["status"] == "in_transit"


def test_out_for_delivery_can_transition_to_delivered(client: TestClient) -> None:
    response = client.patch("/api/shipments/HL-4412", json={"status": "delivered"})

    assert response.status_code == 200
    assert response.json()["status"] == "delivered"
    assert response.json()["id"] == "HL-4412"
