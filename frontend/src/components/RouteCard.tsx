import type { RouteAlternative } from "../types/trip";

type RouteCardProps = { route: RouteAlternative };

const modeIcons: Record<string, string> = { auto: "A", cab: "C", bus: "B", metro: "M", walking: "W" };

export function RouteCard({ route }: RouteCardProps) {
  return (
    <article className={`route-card ${route.is_recommended ? "route-card-recommended" : ""}`}>
      <div className="flex items-start gap-4">
        <div className="mode-icon">{modeIcons[route.mode_code] ?? "·"}</div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-display text-2xl">{route.mode_name}</h3>
            {route.is_recommended && <span className="recommendation-label">Recommended</span>}
          </div>
          <p className="mt-1 text-sm text-ink/60">{route.distance_km} km route · score {route.score.toFixed(2)}</p>
        </div>
        <div className="text-right"><p className="font-display text-2xl">₹{Math.round(route.estimated_cost_min_inr)}–{Math.round(route.estimated_cost_max_inr)}</p><p className="text-xs uppercase tracking-[0.12em] text-ink/50">estimated fare</p></div>
      </div>
      <div className="mt-6 grid grid-cols-3 gap-2 border-y border-ink/10 py-4 text-sm">
        <div><p className="text-ink/50">Time</p><strong>{route.duration_min} min</strong></div>
        <div><p className="text-ink/50">Walking</p><strong>{route.walking_distance_m} m</strong></div>
        <div><p className="text-ink/50">Transfers</p><strong>{route.transfers}</strong></div>
      </div>
      <p className="mt-4 text-sm leading-6 text-ink/70">{route.explanation}</p>
      <p className="mt-3 text-xs font-bold uppercase tracking-[0.12em] text-moss">{route.accessible ? "Accessible data available" : "Accessibility not confirmed"}</p>
    </article>
  );
}
