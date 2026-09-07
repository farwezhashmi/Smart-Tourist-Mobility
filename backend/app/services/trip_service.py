from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.schemas.trip import TripSearchRequest, TripSearchResponse
from app.services.location_service import _location_response, get_location
from app.services.route_service import find_route_alternatives


def search_trip(db: Session, request: TripSearchRequest) -> TripSearchResponse:
    try:
        source = get_location(db, request.source_location_id)
        destination = get_location(db, request.destination_location_id)
    except ValueError as exc:
        raise LookupError(str(exc)) from exc

    alternatives = find_route_alternatives(db, request, source, destination)
    return TripSearchResponse(
        source=_location_response(source),
        destination=_location_response(destination),
        preference=request.preference,
        alternatives=alternatives,
        recommended_route_id=alternatives[0].id,
    )
