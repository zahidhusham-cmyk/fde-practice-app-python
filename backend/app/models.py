from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str] = mapped_column(String, nullable=False)
    vehicle: Mapped[str] = mapped_column(String, nullable=False)


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer: Mapped[str] = mapped_column(String, nullable=False)
    origin_city: Mapped[str] = mapped_column(String, nullable=False)
    origin_state: Mapped[str] = mapped_column(String, nullable=False)
    destination_city: Mapped[str] = mapped_column(String, nullable=False)
    destination_state: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    service_level: Mapped[str] = mapped_column(String, nullable=False)
    promised_on: Mapped[date] = mapped_column(Date, nullable=False)
    weight_lb: Mapped[int] = mapped_column(Integer, nullable=False)
    pieces: Mapped[int] = mapped_column(Integer, nullable=False)
    driver_id: Mapped[str | None] = mapped_column(ForeignKey("drivers.id"), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    driver: Mapped[Driver | None] = relationship()
    events: Mapped[list["ShipmentEvent"]] = relationship(
        back_populates="shipment",
        order_by="ShipmentEvent.timestamp",
        cascade="all, delete-orphan",
    )


class ShipmentEvent(Base):
    __tablename__ = "shipment_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shipment_id: Mapped[str] = mapped_column(ForeignKey("shipments.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    shipment: Mapped[Shipment] = relationship(back_populates="events")
