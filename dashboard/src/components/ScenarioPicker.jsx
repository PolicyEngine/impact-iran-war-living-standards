"use client";

import { colors } from "../lib/colors";
import { getScenarioGroups } from "../lib/scenarioContent";

export function ScenarioTypeBadge({ label }) {
  if (!label) return null;
  return (
    <span className="mr-2 inline-block rounded-full border border-slate-300 bg-white px-2.5 py-0.5 text-xs font-semibold uppercase tracking-[0.06em] text-slate-600">
      {label}
    </span>
  );
}

// Grouped by type, forecast-based first, so the stress tests are labelled
// as stress tests where the reader chooses between them.
export function ScenarioButtons({ data, selected, onSelect }) {
  return (
    <div className="space-y-3">
      {getScenarioGroups(data).map((group) => (
        <div key={group.type} role="group" aria-label={group.label}>
          <div className="mb-1.5 text-xs font-medium uppercase tracking-[0.08em] text-slate-500">
            {group.label}
          </div>
          <div className="flex flex-wrap gap-2">
            {group.options.map((s) => (
              <button
                key={s.id}
                className={`rounded-full px-5 py-2 text-sm font-medium transition-colors ${
                  selected === s.id
                    ? "text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
                style={
                  selected === s.id
                    ? { backgroundColor: colors.primary[800] }
                    : undefined
                }
                onClick={() => onSelect(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
