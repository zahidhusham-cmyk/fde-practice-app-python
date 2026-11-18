from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ShipmentNotFound, ShipmentValidationError
from app.schemas import (
    Pagination,
    ShipmentDetail,
    ShipmentListItem,
    ShipmentListOut,
    ShipmentUpdate,
)
from app.services.shipments import ShipmentService

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


def _parse_page(page: int) -> int:
    return page if page >= 1 else 1


def _parse_limit(limit: int) -> int:
    if limit < 1:
        return 10
    return min(limit, 50)


@router.get("", response_model=ShipmentListOut)
def list_shipments(
    page: int = Query(1),
    limit: int = Query(10),
    db: Session = Depends(get_db),
) -> ShipmentListOut:
    page = _parse_page(page)
    limit = _parse_limit(limit)
    shipments, total = ShipmentService(db).list_shipments(page=page, limit=limit)
    total_pages = max(1, (total + limit - 1) // limit)
    return ShipmentListOut(
        shipments=[ShipmentListItem.model_validate(item) for item in shipments],
        pagination=Pagination(page=page, limit=limit, total=total, total_pages=total_pages),
    )


@router.get("/{shipment_id}", response_model=ShipmentDetail)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)) -> ShipmentDetail:
    try:
        shipment = ShipmentService(db).get_shipment(shipment_id)
    except ShipmentNotFound:
        raise HTTPException(status_code=404, detail="Shipment not found") from None
    return ShipmentDetail.model_validate(shipment)


@router.patch("/{shipment_id}", response_model=ShipmentDetail)
def update_shipment(
    shipment_id: str,
    payload: ShipmentUpdate,
    db: Session = Depends(get_db),
) -> ShipmentDetail:
    service = ShipmentService(db)
    try:
        shipment = service.update_shipment(shipment_id, payload)
    except ShipmentNotFound:
        raise HTTPException(status_code=404, detail="Shipment not found") from None
    except ShipmentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return ShipmentDetail.model_validate(shipment)
