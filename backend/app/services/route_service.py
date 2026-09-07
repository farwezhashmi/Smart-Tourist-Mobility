from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Location, Route, TransportMode
from app.schemas.trip import Preference, RouteAlternative, TripSearchRequest


WEIGHTS: dict[Preference, dict[str, float]] = {
    "cheapest": {"cost": 0.55, "time": 0.15, "walking": 0.10, "transfers": 0.10, "emissions": 0.10},
    "fastest": {"cost": 0.10, "time": 0.60, "walking": 0.10, "transfers": 0.10, "emissions": 0.10},
    "balanced": {"cost": 0.30, "time": 0.30, "walking": 0.15, "transfers": 0.15, "emissions": 0.10},
    "least_walking": {"cost": 0.15, "time": 0.20, "walking": 0.50, "transfers": 0.10, "emissions": 0.05},
    "eco_friendly": {"cost": 0.15, "time": 0.20, "walking": 0.15, "transfers": 0.10, "emissions": 0.40},
}


@dataclass
class Candidate:
    route: Route
    mode: TransportMode
    cost_min: float
    cost_max: float
    emissions: float
    score: float = 0.0


def find_route_alternatives(db: Session, request: TripSearchRequest, source: Location, destination: Location) -> list[RouteAlternative]:
    rows = db.execute(
        select(Route, TransportMode)
        .join(TransportMode, Route.mode_id == TransportMode.id)
        .where(Route.origin_location_id == source.id, Route.destination_location_id == destination.id)
    ).all()
    if not rows:
        raise LookupError("No route alternatives are available for this trip")

    candidates = [_candidate(route, mode, request.passengers) for route, mode in rows]
    candidates = [candidate for candidate in candidates if candidate.route.walking_distance_m <= request.max_walking_distance_m]
    if request.accessibility_required:
        candidates = [candidate for candidate in candidates if candidate.route.is_accessible and candidate.mode.supports_accessibility]
    if request.budget_inr is not None:
        candidates = [candidate for candidate in candidates if candidate.cost_min <= request.budget_inr]
    if not candidates:
        raise LookupError("No route matches the selected walking, accessibility, or budget constraints")

    _score_candidates(candidates, request.preference)
    candidates.sort(key=lambda candidate: candidate.score)
    recommendation = candidates[0]
    return [_to_response(candidate, candidate is recommendation, request.preference) for candidate in candidates]


def _candidate(route: Route, mode: TransportMode, passengers: int) -> Candidate:
    base_cost = _base_cost(mode.code, float(route.distance_km))
    passenger_factor = 1 + max(passengers - 1, 0) * (0.15 if mode.code in {"cab", "auto"} else 0.05)
    cost_min = round(base_cost * passenger_factor, 2)
    cost_max = round(cost_min * 1.20, 2)
    emissions = float(route.distance_km) * float(mode.emission_factor_g_per_km or 0)
    return Candidate(route, mode, cost_min, cost_max, emissions)


def _base_cost(mode_code: str, distance_km: float) -> float:
    if mode_code == "walking":
        return 0
    if mode_code == "metro":
        return 20 + distance_km * 2.5
    if mode_code == "bus":
        return 15 + distance_km * 1.8
    if mode_code == "auto":
        return 30 + distance_km * 16
    if mode_code == "cab":
        return 80 + distance_km * 20
    return 40 + distance_km * 15


def _score_candidates(candidates: list[Candidate], preference: Preference) -> None:
    weights = WEIGHTS[preference]
    max_cost = max(candidate.cost_max for candidate in candidates) or 1
    max_time = max(float(candidate.route.duration_min) for candidate in candidates) or 1
    max_walking = max(float(candidate.route.walking_distance_m) for candidate in candidates) or 1
    max_transfers = max(candidate.route.transfer_count for candidate in candidates) or 1
    max_emissions = max(candidate.emissions for candidate in candidates) or 1
    for candidate in candidates:
        candidate.score = round(
            weights["cost"] * candidate.cost_max / max_cost
            + weights["time"] * float(candidate.route.duration_min) / max_time
            + weights["walking"] * float(candidate.route.walking_distance_m) / max_walking
            + weights["transfers"] * candidate.route.transfer_count / max_transfers
            + weights["emissions"] * candidate.emissions / max_emissions,
            4,
        )


def _to_response(candidate: Candidate, recommended: bool, preference: Preference) -> RouteAlternative:
    route = candidate.route
    mode = candidate.mode
    return RouteAlternative(
        id=route.id,
        mode_code=mode.code,
        mode_name=mode.name,
        estimated_cost_min_inr=candidate.cost_min,
        estimated_cost_max_inr=candidate.cost_max,
        duration_min=round(float(route.duration_min)),
        walking_distance_m=round(float(route.walking_distance_m)),
        transfers=route.transfer_count,
        accessible=route.is_accessible and mode.supports_accessibility,
        distance_km=round(float(route.distance_km), 1),
        score=candidate.score,
        is_recommended=recommended,
        explanation=_explanation(candidate, recommended, preference),
    )


def _explanation(candidate: Candidate, recommended: bool, preference: Preference) -> str:
    if recommended:
        return f"Recommended for {preference.replace('_', ' ')}: approximately INR {candidate.cost_min:.0f}-{candidate.cost_max:.0f}, with {round(float(candidate.route.duration_min))} minutes of travel."
    return f"Alternative at approximately INR {candidate.cost_min:.0f}-{candidate.cost_max:.0f}, taking {round(float(candidate.route.duration_min))} minutes."
