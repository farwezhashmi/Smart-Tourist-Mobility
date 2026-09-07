from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.trip import LocationResponse, TransportModeResponse, TripSearchRequest, TripSearchResponse
from app.services.location_service import list_locations, list_transport_modes
from app.services.trip_service import search_trip

router = APIRouter(tags=["trips"])


@router.get("/locations", response_model=list[LocationResponse])
def locations(db: Session = Depends(get_db)) -> list[LocationResponse]:
    return list_locations(db)


@router.get("/transport-modes", response_model=list[TransportModeResponse])
def transport_modes(db: Session = Depends(get_db)) -> list[TransportModeResponse]:
    return list_transport_modes(db)


@router.post("/trips/search", response_model=TripSearchResponse)
def trip_search(request: TripSearchRequest, db: Session = Depends(get_db)) -> TripSearchResponse:
    try:
        return search_trip(db, request)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
