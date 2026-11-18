from fastapi.testclient import TestClient


def test_lists_drivers(client: TestClient) -> None:
    response = client.get("/api/drivers")

    assert response.status_code == 200
    drivers = response.json()["drivers"]
    assert len(drivers) == 6
    ids = {driver["id"] for driver in drivers}
    assert "drv-maya" in ids
    assert all({"id", "name", "email", "region", "vehicle"} <= driver.keys() for driver in drivers)
