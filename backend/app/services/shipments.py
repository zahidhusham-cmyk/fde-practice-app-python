from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.exceptions import ShipmentNotFound, ShipmentValidationError
from app.models import Shipment, ShipmentEvent
from app.repositories.drivers import DriverRepository
from app.repositories.shipments import ShipmentRepository
from app.schemas import ShipmentUpdate

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "booked": {"at_origin", "cancelled"},
    "at_origin": {"in_transit", "cancelled"},
    "in_transit": {"at_hub", "out_for_delivery", "delayed"},
    "at_hub": {"out_for_delivery", "delayed"},
    "out_for_delivery": {"delayed", "cancelled"},
    "delayed": {"in_transit", "at_hub", "out_for_delivery", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
}


class ShipmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ShipmentRepository(db)
        self.drivers = DriverRepository(db)

    def list_shipments(self, *, page: int, limit: int) -> tuple[list[Shipment], int]:
        offset = (page - 1) * limit
        return self.repo.list(offset=offset, limit=limit)

    def get_shipment(self, shipment_id: str) -> Shipment:
        shipment = self.repo.get(shipment_id)
        if shipment is None:
            raise ShipmentNotFound()
        return shipment

    def update_shipment(self, shipment_id: str, patch: ShipmentUpdate) -> Shipment:
        shipment = self.get_shipment(shipment_id)

        if not patch.model_fields_set:
            raise ShipmentValidationError("Expected at least one of: status, driver_id")

        if "status" in patch.model_fields_set and patch.status is not None:
            new_status = patch.status.value
            current = shipment.status
            if new_status != current:
                allowed = ALLOWED_TRANSITIONS.get(current, set())
                if new_status not in allowed:
                    raise ShipmentValidationError(
                        f"Cannot transition from {current} to {new_status}"
                    )
                shipment.status = new_status
                shipment.events.append(
                    ShipmentEvent(
                        timestamp=_utcnow(),
                        location=None,
                        message=f"Status updated to {new_status.replace('_', ' ')}.",
                    )
                )

        if "driver_id" in patch.model_fields_set:
            if patch.driver_id is not None and self.drivers.get(patch.driver_id) is None:
                raise ShipmentValidationError("driver_id must be a valid driver id or null")
            shipment.driver_id = patch.driver_id

        shipment.updated_at = _utcnow()
        return self.repo.save(shipment)


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
