import { useEffect, useState } from "react";
import axios from "axios";

import { fetchLocations, searchTrip } from "../lib/api";
import type { Location, TripSearchRequest, TripSearchResponse } from "../types/trip";
import { RouteCard } from "../components/RouteCard";
import { TripForm } from "../components/TripForm";

const initialForm: TripSearchRequest = {
  source_location_id: "",
  destination_location_id: "",
  passengers: 1,
  preference: "balanced",
  max_walking_distance_m: 800,
  accessibility_required: false,
  budget_inr: null,
};

export default function TripPlanner() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState<TripSearchResponse | null>(null);
  const [loadingLocations, setLoadingLocations] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLocations()
      .then((items) => {
        setLocations(items);
        const source = items.find((item) => item.name === "Secunderabad Railway Station");
        const destination = items.find((item) => item.name === "Charminar");
        setForm((current) => ({ ...current, source_location_id: source?.id ?? "", destination_location_id: destination?.id ?? "" }));
      })
      .catch(() => setError("Locations could not be loaded from the mobility API."))
      .finally(() => setLoadingLocations(false));
  }, []);

  async function handleSearch() {
    setError(null);
    setResult(null);
    setSearching(true);
    try {
      setResult(await searchTrip(form));
    } catch (requestError: unknown) {
      if (axios.isAxiosError(requestError) && requestError.response?.data?.detail) {
        setError(requestError.response.data.detail);
      } else {
        setError("The trip search could not be completed. Check that the backend is running.");
      }
    } finally {
      setSearching(false);
    }
  }

  return (
    <main className="min-h-screen bg-paper text-ink">
      <header className="border-b border-ink/10 bg-ink text-paper">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-12"><div><p className="text-xs font-bold uppercase tracking-[0.28em] text-saffron">Smart Tourist Mobility</p><p className="mt-1 text-sm text-paper/60">Hyderabad · Phase 2 trip planner</p></div><span className="rounded-full border border-paper/20 px-3 py-1 text-xs font-bold uppercase tracking-[0.12em]">Decision support</span></div>
      </header>
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-10 lg:grid-cols-[minmax(0,0.92fr)_minmax(420px,1.08fr)] lg:px-12 lg:py-14">
        <section className="animate-rise">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-moss">Plan the ride, understand the choice</p>
          <h1 className="mt-4 max-w-2xl font-display text-5xl leading-[0.98] sm:text-6xl">Your next Hyderabad journey, compared honestly.</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-ink/65">Tell us what matters today. We will compare the route records available for your trip and show the trade-offs behind each option.</p>
          <div className="mt-10 grid max-w-xl grid-cols-3 gap-3"><div className="metric"><span>Live</span><strong>API route data</strong></div><div className="metric"><span>5</span><strong>preferences</strong></div><div className="metric"><span>6</span><strong>demo corridors</strong></div></div>
        </section>
        <section className="panel animate-rise-delayed">
          <div className="mb-7 flex items-end justify-between border-b border-ink/10 pb-5"><div><p className="eyebrow">Trip planner</p><h2 className="mt-2 font-display text-3xl">Where are you headed?</h2></div><span className="text-xs font-bold uppercase tracking-[0.15em] text-ink/45">Hyderabad MVP</span></div>
          {loadingLocations ? <div className="rounded-2xl bg-saffron/15 p-5 text-sm">Loading live locations...</div> : <TripForm locations={locations} value={form} onChange={setForm} onSubmit={handleSearch} disabled={searching} />}
          {error && <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-800" role="alert">{error}</div>}
        </section>
      </div>
      {result && <section className="border-t border-ink/10 bg-white/55"><div className="mx-auto max-w-7xl px-6 py-10 lg:px-12"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="eyebrow">Routes from the API</p><h2 className="mt-2 font-display text-4xl">{result.source.name} <span className="text-moss">to</span> {result.destination.name}</h2></div><p className="max-w-sm text-right text-sm leading-6 text-ink/60">Ranked for <strong className="text-ink">{result.preference.replace("_", " ")}</strong>. Costs are estimates from the current demo route data.</p></div><div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">{result.alternatives.map((route) => <RouteCard key={route.id} route={route} />)}</div></div></section>}
    </main>
  );
}
