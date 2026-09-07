from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


Preference = Literal["cheapest", "fastest", "balanced", "least_walking", "eco_friendly"]


class TripSearchRequest(BaseModel):
    source_location_id: UUID
    destination_location_id: UUID
    passengers: int = Field(default=1, ge=1, le=20)
    preference: Preference = "balanced"
    max_walking_distance_m: float = Field(default=800, ge=0, le=50000)
    accessibility_required: bool = False
    budget_inr: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def locations_must_differ(self) -> "TripSearchRequest":
        if self.source_location_id == self.destination_location_id:
            raise ValueError("Source and destination must be different")
        return self


class LocationResponse(BaseModel):
    id: UUID
    name: str
    location_type: str
    zone: str
    latitude: float
    longitude: float
    accessibility_notes: str | None


class TransportModeResponse(BaseModel):
    id: UUID
    code: str
    name: str
    is_public: bool
    supports_accessibility: bool


class RouteAlternative(BaseModel):
    id: UUID
    mode_code: str
    mode_name: str
    estimated_cost_min_inr: float
    estimated_cost_max_inr: float
    duration_min: int
    walking_distance_m: int
    transfers: int
    accessible: bool
    distance_km: float
    score: float
    is_recommended: bool
    explanation: str


class TripSearchResponse(BaseModel):
    source: LocationResponse
    destination: LocationResponse
    preference: Preference
    alternatives: list[RouteAlternative]
    recommended_route_id: UUID
