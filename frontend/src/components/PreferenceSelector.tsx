import type { Preference } from "../types/trip";

type PreferenceSelectorProps = {
  value: Preference;
  onChange: (value: Preference) => void;
};

const preferences: Array<{ value: Preference; label: string; note: string }> = [
  { value: "cheapest", label: "Cheapest", note: "Keep spend low" },
  { value: "fastest", label: "Fastest", note: "Arrive sooner" },
  { value: "balanced", label: "Balanced", note: "A sensible middle" },
  { value: "least_walking", label: "Least walking", note: "Reduce foot distance" },
  { value: "eco_friendly", label: "Eco friendly", note: "Prefer lower emissions" },
];

export function PreferenceSelector({ value, onChange }: PreferenceSelectorProps) {
  return (
    <fieldset>
      <legend className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-ink/55">Travel preference</legend>
      <div className="grid gap-2 sm:grid-cols-5">
        {preferences.map((preference) => (
          <button
            type="button"
            key={preference.value}
            onClick={() => onChange(preference.value)}
            className={`preference-button ${value === preference.value ? "preference-button-active" : ""}`}
          >
            <span className="block font-bold">{preference.label}</span>
            <span className="mt-1 block text-xs font-normal opacity-70">{preference.note}</span>
          </button>
        ))}
      </div>
    </fieldset>
  );
}
