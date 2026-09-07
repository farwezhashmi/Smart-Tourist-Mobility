import type { Location } from "../types/trip";

type LocationSelectorProps = {
  label: string;
  value: string;
  locations: Location[];
  onChange: (value: string) => void;
};

export function LocationSelector({ label, value, locations, onChange }: LocationSelectorProps) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-bold uppercase tracking-[0.16em] text-ink/55">{label}</span>
      <select className="field" value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Choose a place</option>
        {locations.map((location) => (
          <option key={location.id} value={location.id}>{location.name} · {location.zone}</option>
        ))}
      </select>
    </label>
  );
}
