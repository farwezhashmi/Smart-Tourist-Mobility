# MVP API Specification

Base path: `/api`

All timestamps are ISO 8601 UTC. Currency is INR and amounts are decimal numbers in rupees. Error responses use:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Passengers must be at least 1",
    "request_id": "uuid"
  }
}
```

## Shared types

### Trip context

```json
{
  "source_location_id": "uuid",
  "destination_location_id": "uuid",
  "passengers": 3,
  "budget_inr": 500.0,
  "preference": "budget",
  "walking_tolerance_m": 800,
  "accessibility_required": false,
  "departure_at": "2026-09-07T10:00:00+05:30"
}
```

Allowed preferences: `cheapest`, `fastest`, `balanced`, `least_walking`, `eco_friendly`, `accessibility`.

## `GET /api/locations`

Query parameters: `q`, `zone`, `limit`.

Returns active Hyderabad locations suitable for a planner selector. The response includes `id`, `name`, `type`, `zone`, `latitude`, and `longitude`.

## `GET /api/transport-modes`

Returns active modes and capabilities, including `id`, `code`, `name`, `is_public`, `supports_accessibility`, and `emission_factor_g_per_km` when available.

## `POST /api/trips/search`

Creates a trip request and returns a combined first-pass result.

Response shape:

```json
{
  "source": { "id": "uuid", "name": "Secunderabad Railway Station", "location_type": "transport_hub", "zone": "Secunderabad", "latitude": 17.4399, "longitude": 78.5011, "accessibility_notes": "..." },
  "destination": { "id": "uuid", "name": "Charminar", "location_type": "attraction", "zone": "Old City", "latitude": 17.3616, "longitude": 78.4747, "accessibility_notes": "..." },
  "preference": "cheapest",
  "recommended_route_id": "uuid",
  "alternatives": [
    {
      "id": "uuid",
      "mode_code": "metro",
      "mode_name": "Metro",
      "estimated_cost_min_inr": 46.75,
      "estimated_cost_max_inr": 56.10,
      "duration_min": 38,
      "walking_distance_m": 350,
      "transfers": 1,
      "accessible": true,
      "distance_km": 9.0,
      "score": 0.31,
      "is_recommended": true,
      "explanation": "Recommended for cheapest: approximately INR 47-56, with 38 minutes of travel."
    }
  ]
}
```

Validation: source and destination must differ, passengers must be 1 or more, budget if supplied must be non-negative, and walking tolerance must be non-negative.

## `POST /api/fare/predict`

Request: trip context plus `vehicle_type`, `distance_km`, `duration_min`, and optional `traffic_level` and `weather_condition`.

Response:

```json
{
  "predicted_fare": 200.0,
  "lower_bound": 180.0,
  "upper_bound": 220.0,
  "currency": "INR",
  "model_version": "baseline-2026-09-01",
  "rule_component": 165.0,
  "ml_component": 205.0,
  "range_method": "residual_quantiles",
  "data_provenance": ["public", "synthetic_demo"]
}
```

The service must reject negative distance/duration and unknown vehicle types. It must label synthetic/demo output when used.

## `POST /api/fare/check`

Request:

```json
{
  "trip_id": "uuid",
  "quoted_fare": 400.0
}
```

Response:

```json
{
  "status": "significantly_above_reference",
  "quoted_fare": 400.0,
  "reference_lower_bound": 180.0,
  "reference_upper_bound": 220.0,
  "deviation_percent_from_upper_bound": 81.8,
  "message": "Quoted fare is significantly above the estimated reference range.",
  "disclaimer": "This is a decision-support estimate, not a fraud determination."
}
```

The service must reject negative quotes and must not use accusatory language.

## `POST /api/routes/optimize`

Request: trip context plus optional `traffic_level`, `weather_condition`, and `max_results`.

Response:

```json
{
  "trip_id": "uuid",
  "optimization_context": {
    "traffic_level": "simulated_high",
    "is_demo_context": true,
    "weights": {
      "cost": 0.45,
      "time": 0.2,
      "walking": 0.15,
      "transfers": 0.1,
      "emissions": 0.1
    }
  },
  "recommended_route_id": "uuid",
  "routes": [
    {
      "route_id": "uuid",
      "rank": 1,
      "label": "Metro + Auto",
      "estimated_cost_min": 130.0,
      "estimated_cost_max": 170.0,
      "duration_min": 48,
      "walking_distance_m": 550,
      "transfers": 1,
      "accessible": false,
      "score": 0.31,
      "legs": []
    }
  ]
}
```

No-route cases return HTTP 404 with code `NO_ROUTE_AVAILABLE`. Scores and weights are returned for explainability.

## `GET /api/trips/{trip_id}`

Returns the persisted trip request, fare prediction, route recommendations, anomaly checks, and context provenance. Unknown IDs return HTTP 404.

## Admin endpoints

The dashboard can initially consume read-only endpoints under `/api/admin/summary`, `/api/admin/routes`, `/api/admin/anomalies`, and `/api/admin/demand`. These require admin authentication and return aggregate data only. Exact response contracts should be added after the base trip flow is passing end to end.

## Status and observability

- `200`: successful read or computation
- `201`: trip or prediction created
- `400`: malformed or invalid domain input
- `401`: missing/invalid admin credentials
- `404`: unknown resource or no route
- `422`: Pydantic validation failure
- `429`: rate limit exceeded
- `500`: unexpected server failure

Every response should expose or log a request ID. Provider failures should become a clear `ROUTING_PROVIDER_UNAVAILABLE` error or a labelled demo fallback, never an unmarked fabricated live result.
