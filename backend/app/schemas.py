from datetime import UTC, date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ShipmentStatus(str, Enum):
    booked = "booked"
    at_origin = "at_origin"
    in_transit = "in_transit"
    at_hub = "at_hub"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    delayed = "delayed"
    cancelled = "cancelled"


class ServiceLevel(str, Enum):
    standard = "standard"
    expedited = "expedited"
    overnight = "overnight"


def _isoformat_z(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    region: str
    vehicle: str


class DriverListOut(BaseModel):
    drivers: list[DriverOut]


class ShipmentEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    location: str | None
    message: str

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        return _isoformat_z(value)


class ShipmentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer: str
    origin_city: str
    origin_state: str
    destination_city: str
    destination_state: str
    status: ShipmentStatus
    service_level: ServiceLevel
    promised_on: date
    weight_lb: int
    pieces: int
    driver_id: str | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetimes(self, value: datetime) -> str:
        return _isoformat_z(value)


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class ShipmentListOut(BaseModel):
    shipments: list[ShipmentListItem]
    pagination: Pagination


class ShipmentDetail(ShipmentListItem):
    notes: str
    events: list[ShipmentEventOut] = Field(default_factory=list)


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus | None = None
    driver_id: str | None = None
