export type Preference = "cheapest" | "fastest" | "balanced" | "least_walking" | "eco_friendly";

export type Location = {
  id: string;
  name: string;
  location_type: string;
  zone: string;
  latitude: number;
  longitude: number;
  accessibility_notes: string | null;
};

export type RouteAlternative = {
  id: string;
  mode_code: string;
  mode_name: string;
  estimated_cost_min_inr: number;
  estimated_cost_max_inr: number;
  duration_min: number;
  walking_distance_m: number;
  transfers: number;
  accessible: boolean;
  distance_km: number;
  score: number;
  is_recommended: boolean;
  explanation: string;
};

export type TripSearchRequest = {
  source_location_id: string;
  destination_location_id: string;
  passengers: number;
  preference: Preference;
  max_walking_distance_m: number;
  accessibility_required: boolean;
  budget_inr: number | null;
};

export type TripSearchResponse = {
  source: Location;
  destination: Location;
  preference: Preference;
  alternatives: RouteAlternative[];
  recommended_route_id: string;
};
