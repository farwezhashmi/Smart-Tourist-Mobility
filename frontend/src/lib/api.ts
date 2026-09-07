import axios from "axios";
import type { Location, TripSearchRequest, TripSearchResponse } from "../types/trip";

const api = axios.create({ baseURL: "/api" });

export async function fetchLocations(): Promise<Location[]> {
  const response = await api.get<Location[]>("/locations");
  return response.data;
}

export async function searchTrip(request: TripSearchRequest): Promise<TripSearchResponse> {
  const response = await api.post<TripSearchResponse>("/trips/search", request);
  return response.data;
}
