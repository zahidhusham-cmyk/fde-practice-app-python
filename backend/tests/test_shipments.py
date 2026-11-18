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


def test_search_matches_customer_case_insensitively(client: TestClient) -> None:
    response = client.get("/api/shipments", params={"q": "bRiGhTlEaF"})

    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body["shipments"]] == ["HL-4412"]
    assert body["shipments"][0]["customer"] == "Brightleaf Market"
    assert body["pagination"]["total"] == 1
    assert body["pagination"]["total"] < 28
    assert body["pagination"]["total_pages"] == 1


def test_search_matches_a_city_before_pagination(client: TestClient) -> None:
    response = client.get("/api/shipments", params={"q": "philadelphia", "limit": 2})

    assert response.status_code == 200
    body = response.json()
    assert len(body["shipments"]) == 2
    assert body["pagination"]["total"] > 2
    assert body["pagination"]["total"] < 28
    assert body["pagination"]["total_pages"] == (body["pagination"]["total"] + 1) // 2
    assert all(
        "philadelphia" in f"{item['origin_city']} {item['destination_city']}".lower()
        for item in body["shipments"]
    )


def test_search_with_no_matches_returns_an_empty_page(client: TestClient) -> None:
    response = client.get("/api/shipments", params={"q": "zzzz-not-a-shipment"})

    assert response.status_code == 200
    body = response.json()
    assert body["shipments"] == []
    assert body["pagination"]["total"] == 0
    assert body["pagination"]["total_pages"] == 1


def test_search_treats_sql_injection_as_plain_text(client: TestClient) -> None:
    payload = "' OR 1=1; DROP TABLE shipments; --"
    response = client.get("/api/shipments", params={"q": payload})

    assert response.status_code == 200
    body = response.json()
    assert body["shipments"] == []
    assert body["pagination"]["total"] == 0

    follow_up = client.get("/api/shipments")
    assert follow_up.status_code == 200
    assert follow_up.json()["pagination"]["total"] == 28


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
    before = client.get("/api/shipments/HL-4412")
    assert before.status_code == 200
    assert before.json()["status"] == "out_for_delivery"
    event_count = len(before.json()["events"])

    response = client.patch("/api/shipments/HL-4412", json={"status": "delivered"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "HL-4412"
    assert body["status"] == "delivered"
    assert len(body["events"]) == event_count + 1
    assert body["events"][-1]["message"] == "Status updated to delivered."

    persisted = client.get("/api/shipments/HL-4412")
    assert persisted.status_code == 200
    assert persisted.json()["status"] == "delivered"


def _new_shipment(**overrides: object) -> dict:
    body = {
        "customer": "Northwind Provisions",
        "origin_city": "Boston",
        "origin_state": "ma",
        "destination_city": "Albany",
        "destination_state": "NY",
        "service_level": "expedited",
        "promised_on": "2026-11-25",
        "weight_lb": 300,
        "pieces": 4,
        "notes": "  Dock opens at 7.  ",
    }
    body.update(overrides)
    return body


def test_books_a_shipment_and_assigns_the_next_id(client: TestClient) -> None:
    first = client.post("/api/shipments", json=_new_shipment())

    assert first.status_code == 201
    body = first.json()
    assert body["id"] == "HL-4429"
    assert body["status"] == "booked"
    assert body["customer"] == "Northwind Provisions"
    assert body["origin_state"] == "MA"
    assert body["notes"] == "Dock opens at 7."
    assert body["driver_id"] is None
    assert body["events"] == [
        {
            "id": body["events"][0]["id"],
            "timestamp": body["events"][0]["timestamp"],
            "location": "Boston, MA",
            "message": "Shipment booked.",
        }
    ]

    second = client.post("/api/shipments", json=_new_shipment(customer="Second Load"))
    assert second.status_code == 201
    assert second.json()["id"] == "HL-4430"


def test_rejects_an_unknown_driver_when_booking(client: TestClient) -> None:
    response = client.post("/api/shipments", json=_new_shipment(driver_id="drv-nobody"))

    assert response.status_code == 400
    assert "driver_id" in response.json()["detail"]


def test_rejects_a_non_positive_weight_when_booking(client: TestClient) -> None:
    response = client.post("/api/shipments", json=_new_shipment(weight_lb=0))

    assert response.status_code == 422

