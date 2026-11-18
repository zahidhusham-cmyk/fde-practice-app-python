from sqlalchemy.orm import Session

from app.models import Driver
from app.repositories.drivers import DriverRepository


class DriverService:
    def __init__(self, db: Session) -> None:
        self.repo = DriverRepository(db)

    def list_drivers(self) -> list[Driver]:
        return self.repo.list()
