import uuid
from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geography
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, Text, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


from app.core.config import get_settings


IS_SQLITE = get_settings().database_url.startswith("sqlite")
POINT_TYPE = Text() if IS_SQLITE else Geography(geometry_type="POINT", srid=4326)
LINE_TYPE = Text() if IS_SQLITE else Geography(geometry_type="LINESTRING", srid=4326)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    location_type: Mapped[str] = mapped_column(Text, nullable=False)
    zone: Mapped[str] = mapped_column(Text, nullable=False)
    point: Mapped[str] = mapped_column(POINT_TYPE, nullable=False)
    accessibility_notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TransportMode(Base):
    __tablename__ = "transport_modes"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(Enum("auto", "cab", "bus", "metro", "walking", "other", name="vehicle_type", create_type=False), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supports_accessibility: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    emission_factor_g_per_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    origin_location_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("locations.id"), nullable=False)
    destination_location_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("locations.id"), nullable=False)
    mode_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), ForeignKey("transport_modes.id"), nullable=False)
    provider: Mapped[str | None] = mapped_column(Text)
    provider_route_id: Mapped[str | None] = mapped_column(Text)
    geometry: Mapped[str | None] = mapped_column(LINE_TYPE)
    distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    duration_min: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    walking_distance_m: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    transfer_count: Mapped[int] = mapped_column(nullable=False, default=0)
    is_accessible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_type: Mapped[str | None] = mapped_column(Text)
    source_reference: Mapped[str | None] = mapped_column(Text)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
