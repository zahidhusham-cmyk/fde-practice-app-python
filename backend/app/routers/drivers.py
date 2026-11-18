from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DriverListOut, DriverOut
from app.services.drivers import DriverService

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.get("", response_model=DriverListOut)
def list_drivers(db: Session = Depends(get_db)) -> DriverListOut:
    drivers = DriverService(db).list_drivers()
    return DriverListOut(drivers=[DriverOut.model_validate(driver) for driver in drivers])
