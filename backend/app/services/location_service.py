from sqlalchemy import select
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from app.db.models import Location, TransportMode
from app.schemas.trip import LocationResponse, TransportModeResponse


def list_locations(db: Session) -> list[LocationResponse]:
    locations = db.scalars(select(Location).where(Location.is_active.is_(True)).order_by(Location.name)).all()
    return [_location_response(location) for location in locations]


def list_transport_modes(db: Session) -> list[TransportModeResponse]:
    modes = db.scalars(select(TransportMode).order_by(TransportMode.name)).all()
    return [TransportModeResponse.model_validate(mode, from_attributes=True) for mode in modes]


def get_location(db: Session, location_id: str) -> Location:
    location = db.get(Location, str(location_id))
    if location is None or not location.is_active:
        raise ValueError("Location was not found")
    return location


def _location_response(location: Location) -> LocationResponse:
    if hasattr(location.point, "data"):
        shape = to_shape(location.point)
        longitude, latitude = shape.x, shape.y
    else:
        point = location.point or "POINT(0 0)"
        longitude, latitude = point.removeprefix("POINT(").removesuffix(")").split()
    return LocationResponse(
        id=location.id,
        name=location.name,
        location_type=location.location_type,
        zone=location.zone,
        latitude=float(latitude),
        longitude=float(longitude),
        accessibility_notes=location.accessibility_notes,
    )
