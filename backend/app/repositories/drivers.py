from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Driver


class DriverRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[Driver]:
        return list(self.db.scalars(select(Driver).order_by(Driver.name.asc())))

    def get(self, driver_id: str) -> Driver | None:
        return self.db.get(Driver, driver_id)
