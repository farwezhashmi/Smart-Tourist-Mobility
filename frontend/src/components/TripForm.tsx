import type { Location, Preference, TripSearchRequest } from "../types/trip";
import { LocationSelector } from "./LocationSelector";
import { PreferenceSelector } from "./PreferenceSelector";

type TripFormProps = {
  locations: Location[];
  value: TripSearchRequest;
  onChange: (value: TripSearchRequest) => void;
  onSubmit: () => void;
  disabled: boolean;
};

export function TripForm({ locations, value, onChange, onSubmit, disabled }: TripFormProps) {
  const update = (patch: Partial<TripSearchRequest>) => onChange({ ...value, ...patch });

  return (
    <form className="space-y-7" onSubmit={(event) => { event.preventDefault(); onSubmit(); }}>
      <div className="grid gap-5 sm:grid-cols-2">
        <LocationSelector label="Starting point" value={value.source_location_id} locations={locations} onChange={(source_location_id) => update({ source_location_id })} />
        <LocationSelector label="Destination" value={value.destination_location_id} locations={locations} onChange={(destination_location_id) => update({ destination_location_id })} />
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <label className="block">
          <span className="mb-2 block text-xs font-bold uppercase tracking-[0.16em] text-ink/55">Passengers</span>
          <input className="field" type="number" min="1" max="20" value={value.passengers} onChange={(event) => update({ passengers: Number(event.target.value) })} />
        </label>
        <label className="block">
          <span className="mb-2 block text-xs font-bold uppercase tracking-[0.16em] text-ink/55">Max walking · metres</span>
          <input className="field" type="number" min="0" max="50000" step="50" value={value.max_walking_distance_m} onChange={(event) => update({ max_walking_distance_m: Number(event.target.value) })} />
        </label>
        <label className="block">
          <span className="mb-2 block text-xs font-bold uppercase tracking-[0.16em] text-ink/55">Budget · INR</span>
          <input className="field" type="number" min="0" step="50" placeholder="No limit" value={value.budget_inr ?? ""} onChange={(event) => update({ budget_inr: event.target.value ? Number(event.target.value) : null })} />
        </label>
      </div>

      <PreferenceSelector value={value.preference} onChange={(preference: Preference) => update({ preference })} />

      <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-ink/10 bg-paper/70 p-4">
        <input className="mt-1 h-4 w-4 accent-moss" type="checkbox" checked={value.accessibility_required} onChange={(event) => update({ accessibility_required: event.target.checked })} />
        <span><strong className="block text-sm">Accessibility-friendly routes</strong><span className="text-sm text-ink/60">Only show options marked accessible in the route data.</span></span>
      </label>

      <button className="primary-button" disabled={disabled} type="submit">{disabled ? "Finding routes..." : "Find my best options"}<span aria-hidden="true">→</span></button>
    </form>
  );
}
