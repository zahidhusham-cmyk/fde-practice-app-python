from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.exceptions import ShipmentNotFound, ShipmentValidationError
from app.models import Shipment, ShipmentEvent
from app.repositories.drivers import DriverRepository
from app.repositories.shipments import ShipmentRepository
from app.schemas import ShipmentCreate, ShipmentStatus, ShipmentUpdate

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "booked": {"at_origin", "cancelled"},
    "at_origin": {"in_transit", "cancelled"},
    "in_transit": {"at_hub", "out_for_delivery", "delayed"},
    "at_hub": {"out_for_delivery", "delayed"},
    "out_for_delivery": {"delivered", "delayed", "cancelled"},
    "delayed": {"in_transit", "at_hub", "out_for_delivery", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
}


class ShipmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ShipmentRepository(db)
        self.drivers = DriverRepository(db)

    def list_shipments(
        self, *, page: int, limit: int, query: str | None = None
    ) -> tuple[list[Shipment], int]:
        offset = (page - 1) * limit
        return self.repo.list(offset=offset, limit=limit, query=query)

    def get_shipment(self, shipment_id: str) -> Shipment:
        shipment = self.repo.get(shipment_id)
        if shipment is None:
            raise ShipmentNotFound()
        return shipment

    def create_shipment(self, payload: ShipmentCreate) -> Shipment:
        if payload.driver_id is not None and self.drivers.get(payload.driver_id) is None:
            raise ShipmentValidationError("driver_id must be a valid driver id or null")

        now = _utcnow()
        shipment = Shipment(
            id=self.repo.next_id(),
            customer=payload.customer,
            origin_city=payload.origin_city,
            origin_state=payload.origin_state,
            destination_city=payload.destination_city,
            destination_state=payload.destination_state,
            status=ShipmentStatus.booked.value,
            service_level=payload.service_level.value,
            promised_on=payload.promised_on,
            weight_lb=payload.weight_lb,
            pieces=payload.pieces,
            driver_id=payload.driver_id,
            notes=payload.notes,
            created_at=now,
            updated_at=now,
            events=[
                ShipmentEvent(
                    timestamp=now,
                    location=f"{payload.origin_city}, {payload.origin_state}",
                    message="Shipment booked.",
                )
            ],
        )
        saved = self.repo.save(shipment)
        created = self.repo.get(saved.id)
        if created is None:
            raise ShipmentNotFound()
        return created

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
