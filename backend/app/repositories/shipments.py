from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Shipment


class ShipmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, *, offset: int, limit: int) -> tuple[list[Shipment], int]:
        total = self.db.scalar(select(func.count()).select_from(Shipment)) or 0
        items = list(
            self.db.scalars(
                select(Shipment).order_by(Shipment.id.asc()).offset(offset).limit(limit)
            )
        )
        return items, total

    def get(self, shipment_id: str) -> Shipment | None:
        return self.db.scalar(
            select(Shipment)
            .options(selectinload(Shipment.events))
            .where(Shipment.id == shipment_id)
        )

    def save(self, shipment: Shipment) -> Shipment:
        self.db.add(shipment)
        self.db.commit()
        self.db.refresh(shipment)
        return shipment
