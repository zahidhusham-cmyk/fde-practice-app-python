from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Shipment

# Columns the shipment search box can match.
SEARCH_COLUMNS = (
    Shipment.id,
    Shipment.customer,
    Shipment.origin_city,
    Shipment.origin_state,
    Shipment.destination_city,
    Shipment.destination_state,
)


def _matches_query(query: str):
    """Case-insensitive substring match across SEARCH_COLUMNS.

    SQLite has no ILIKE, so both sides are lowercased. The % wildcards mean
    the text can appear anywhere in a column, not only at the start.
    """
    pattern = f"%{query.casefold()}%"
    column_matches = (func.lower(column).like(pattern) for column in SEARCH_COLUMNS)
    return or_(*column_matches)


class ShipmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self, *, offset: int, limit: int, query: str | None = None
    ) -> tuple[list[Shipment], int]:
        items_stmt = select(Shipment)
        count_stmt = select(func.count()).select_from(Shipment)

        # Filter the page and the count with the same condition. Pagination
        # happens after this, so total describes the matches, not the full board.
        if query:
            matches = _matches_query(query)
            items_stmt = items_stmt.where(matches)
            count_stmt = count_stmt.where(matches)

        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(
                items_stmt.order_by(Shipment.id.asc()).offset(offset).limit(limit)
            )
        )
        return items, total

    def next_id(self) -> str:
        highest = 4400
        for shipment_id in self.db.scalars(select(Shipment.id)):
            prefix, _, number = shipment_id.partition("-")
            if prefix == "HL" and number.isdigit():
                highest = max(highest, int(number))
        return f"HL-{highest + 1}"

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
