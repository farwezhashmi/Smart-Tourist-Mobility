-- Smart Tourist Mobility - initial PostgreSQL/PostGIS schema
-- Canonical Phase 1 data model. Run after enabling the postgis extension.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE source_type AS ENUM ('official', 'public', 'team_collected', 'synthetic_demo');
CREATE TYPE vehicle_type AS ENUM ('auto', 'cab', 'bus', 'metro', 'walking', 'other');
CREATE TYPE preference_type AS ENUM ('cheapest', 'fastest', 'balanced', 'least_walking', 'eco_friendly', 'accessibility');
CREATE TYPE traffic_level AS ENUM ('low', 'medium', 'high', 'unknown', 'simulated_low', 'simulated_high');
CREATE TYPE trip_status AS ENUM ('created', 'planned', 'completed', 'cancelled');
CREATE TYPE anomaly_status AS ENUM ('within_reference', 'near_upper_bound', 'significantly_above_reference');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE,
    display_name TEXT,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    location_type TEXT NOT NULL,
    zone TEXT NOT NULL,
    point GEOGRAPHY(Point, 4326) NOT NULL,
    accessibility_notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE transport_modes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code vehicle_type NOT NULL UNIQUE,
    name TEXT NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    supports_accessibility BOOLEAN NOT NULL DEFAULT FALSE,
    emission_factor_g_per_km NUMERIC(10, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_location_id UUID NOT NULL REFERENCES locations(id),
    destination_location_id UUID NOT NULL REFERENCES locations(id),
    mode_id UUID NOT NULL REFERENCES transport_modes(id),
    provider TEXT NOT NULL,
    provider_route_id TEXT,
    geometry GEOGRAPHY(LineString, 4326),
    distance_km NUMERIC(10, 3) NOT NULL CHECK (distance_km > 0),
    duration_min NUMERIC(10, 2) NOT NULL CHECK (duration_min > 0),
    walking_distance_m NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (walking_distance_m >= 0),
    transfer_count INTEGER NOT NULL DEFAULT 0 CHECK (transfer_count >= 0),
    is_accessible BOOLEAN NOT NULL DEFAULT FALSE,
    source_type source_type NOT NULL,
    source_reference TEXT,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (origin_location_id <> destination_location_id)
);

CREATE TABLE fare_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    observed_at TIMESTAMPTZ NOT NULL,
    source_location_id UUID NOT NULL REFERENCES locations(id),
    destination_location_id UUID NOT NULL REFERENCES locations(id),
    source_zone TEXT NOT NULL,
    destination_zone TEXT NOT NULL,
    mode_id UUID NOT NULL REFERENCES transport_modes(id),
    distance_km NUMERIC(10, 3) NOT NULL CHECK (distance_km > 0),
    duration_min NUMERIC(10, 2) NOT NULL CHECK (duration_min > 0),
    local_hour SMALLINT NOT NULL CHECK (local_hour BETWEEN 0 AND 23),
    day_of_week SMALLINT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    weekend_flag BOOLEAN NOT NULL,
    traffic_level traffic_level NOT NULL DEFAULT 'unknown',
    weather_condition TEXT,
    passengers INTEGER NOT NULL CHECK (passengers > 0),
    reference_fare NUMERIC(10, 2) NOT NULL CHECK (reference_fare >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    source_type source_type NOT NULL,
    source_reference TEXT,
    collection_method TEXT NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    quality_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (source_location_id <> destination_location_id),
    CHECK (currency = 'INR')
);

CREATE TABLE trip_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    source_location_id UUID NOT NULL REFERENCES locations(id),
    destination_location_id UUID NOT NULL REFERENCES locations(id),
    passengers INTEGER NOT NULL CHECK (passengers > 0),
    budget_inr NUMERIC(10, 2) CHECK (budget_inr >= 0),
    preference preference_type NOT NULL DEFAULT 'balanced',
    walking_tolerance_m NUMERIC(10, 2) NOT NULL DEFAULT 800 CHECK (walking_tolerance_m >= 0),
    accessibility_required BOOLEAN NOT NULL DEFAULT FALSE,
    departure_at TIMESTAMPTZ NOT NULL,
    traffic_level traffic_level NOT NULL DEFAULT 'unknown',
    weather_condition TEXT,
    status trip_status NOT NULL DEFAULT 'created',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (source_location_id <> destination_location_id)
);

CREATE TABLE fare_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_request_id UUID NOT NULL REFERENCES trip_requests(id) ON DELETE CASCADE,
    mode_id UUID REFERENCES transport_modes(id),
    predicted_fare NUMERIC(10, 2) NOT NULL CHECK (predicted_fare >= 0),
    lower_bound NUMERIC(10, 2) NOT NULL CHECK (lower_bound >= 0),
    upper_bound NUMERIC(10, 2) NOT NULL CHECK (upper_bound >= lower_bound),
    model_version TEXT NOT NULL,
    rule_component NUMERIC(10, 2),
    ml_component NUMERIC(10, 2),
    range_method TEXT NOT NULL,
    data_provenance source_type[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE route_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_request_id UUID NOT NULL REFERENCES trip_requests(id) ON DELETE CASCADE,
    route_id UUID NOT NULL REFERENCES routes(id),
    rank INTEGER NOT NULL CHECK (rank > 0),
    score NUMERIC(12, 6) NOT NULL CHECK (score >= 0),
    cost_min_inr NUMERIC(10, 2) NOT NULL CHECK (cost_min_inr >= 0),
    cost_max_inr NUMERIC(10, 2) NOT NULL CHECK (cost_max_inr >= cost_min_inr),
    duration_min NUMERIC(10, 2) NOT NULL CHECK (duration_min > 0),
    walking_distance_m NUMERIC(10, 2) NOT NULL CHECK (walking_distance_m >= 0),
    transfer_count INTEGER NOT NULL CHECK (transfer_count >= 0),
    weights JSONB NOT NULL,
    explanation TEXT NOT NULL,
    is_selected BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE anomaly_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_request_id UUID NOT NULL REFERENCES trip_requests(id) ON DELETE CASCADE,
    fare_prediction_id UUID NOT NULL REFERENCES fare_predictions(id) ON DELETE CASCADE,
    quoted_fare NUMERIC(10, 2) NOT NULL CHECK (quoted_fare >= 0),
    status anomaly_status NOT NULL,
    deviation_percent NUMERIC(10, 2),
    message TEXT NOT NULL,
    disclaimer TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX locations_point_gix ON locations USING GIST (point);
CREATE INDEX locations_zone_idx ON locations (zone) WHERE is_active;
CREATE INDEX routes_origin_destination_idx ON routes (origin_location_id, destination_location_id);
CREATE INDEX fare_observations_context_idx ON fare_observations (observed_at, mode_id, source_type);
CREATE INDEX trip_requests_created_idx ON trip_requests (created_at DESC);
CREATE INDEX fare_predictions_trip_idx ON fare_predictions (trip_request_id, created_at DESC);
CREATE INDEX route_recommendations_trip_rank_idx ON route_recommendations (trip_request_id, rank);
CREATE INDEX anomaly_alerts_status_idx ON anomaly_alerts (status, created_at DESC);
