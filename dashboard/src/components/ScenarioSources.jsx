"use client";

import { formatSourceDate } from "../lib/formatters";
import { getScenarioType } from "../lib/scenarioContent";

// The four registry parameters, in the order a reader meets them.
export const SOURCE_ROWS = [
  { key: "cap_increase_pct", label: "Energy spending", unit: "%" },
  { key: "fuel_pct", label: "Petrol and diesel", unit: "%" },
  { key: "food_increase_pct", label: "Food", unit: "%" },
  { key: "cpi_increase_pp", label: "CPI addition", unit: "pp" },
];

function capitalise(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
}

function isUsableEntry(entry) {
  return (
    entry &&
    Number.isFinite(entry.value) &&
    typeof entry.source_url === "string" &&
    entry.source_url.startsWith("https://") &&
    typeof entry.source_name === "string" &&
    entry.source_name.trim() !== ""
  );
}

/**
 * Where each of a scenario's figures comes from: its source, the date that
 * source published it, and whether it is a published forecast or this
 * study's judgement. Read entirely from the results file's parameter
 * registry, so the citation shown is the one the model ran with.
 */
export default function ScenarioSources({ data, scenario }) {
  const registry = data?.parameters?.registry?.[scenario]?.parameters;
  if (!registry) return null;
  const rows = SOURCE_ROWS.map((row) => ({ ...row, entry: registry[row.key] })).filter(
    (row) => isUsableEntry(row.entry),
  );
  if (rows.length === 0) return null;

  const isForecast = getScenarioType(scenario, data) === "forecast";
  const vintage = data?.metadata?.forecast_vintage;

  return (
    <div className="section-card" data-testid="scenario-sources">
      <h3 className="text-lg font-semibold text-slate-900">
        Where each figure comes from
      </h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        {isForecast ? (
          <>
            Each price is built from a published forecast
            {vintage?.as_of ? `, as of ${formatSourceDate(vintage.as_of)}` : ""}. The
            basis column says where this study&apos;s own pass-through sits between the
            forecast and the figure.
          </>
        ) : (
          <>
            <strong>A stress test, not a forecast:</strong> price levels this study chose,
            anchored to the sources below.
          </>
        )}
      </p>
      <div className="mt-4 overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Assumption</th>
              <th style={{ textAlign: "right" }}>Value</th>
              <th>Basis</th>
              <th>Source</th>
              <th>Published</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ key, label, unit, entry }) => (
              <tr key={key}>
                <td className="font-medium">{label}</td>
                <td style={{ textAlign: "right" }}>
                  +{entry.value}
                  {unit}
                </td>
                <td>{capitalise(entry.basis_label || entry.basis)}</td>
                <td className="text-xs text-slate-600">
                  <a
                    href={entry.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="underline"
                  >
                    {entry.source_name}
                  </a>
                  {entry.source_figure ? (
                    <div className="mt-1">{entry.source_figure}</div>
                  ) : null}
                  {entry.reference_period ? (
                    <div className="mt-1 text-slate-500">
                      Period: {entry.reference_period}
                    </div>
                  ) : null}
                  {entry.supporting_sources?.length ? (
                    <div className="mt-1 text-slate-500">
                      Also:{" "}
                      {entry.supporting_sources.map((s, i) => (
                        <span key={s.url}>
                          {i > 0 ? "; " : ""}
                          <a href={s.url} target="_blank" rel="noreferrer" className="underline">
                            {s.name}
                          </a>
                        </span>
                      ))}
                    </div>
                  ) : null}
                  {entry.derivation ? (
                    <details className="mt-1">
                      <summary className="cursor-pointer text-slate-500">
                        How this figure is derived
                      </summary>
                      <p className="mt-1 leading-5">{entry.derivation}</p>
                    </details>
                  ) : null}
                </td>
                <td className="whitespace-nowrap">{formatSourceDate(entry.source_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isForecast && Array.isArray(vintage?.assumptions) && vintage.assumptions.length > 0 ? (
        <div className="mt-4 text-sm leading-6 text-slate-600">
          <div className="font-semibold text-slate-800">What this scenario assumes</div>
          <ul className="mt-1 list-disc space-y-1 pl-5">
            {vintage.assumptions.map((assumption) => (
              <li key={assumption}>{assumption}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {isForecast && Array.isArray(vintage?.gaps) && vintage.gaps.length > 0 ? (
        <div className="mt-4 text-sm leading-6 text-slate-600">
          <div className="font-semibold text-slate-800">What the forecasts do not cover</div>
          <ul className="mt-1 list-disc space-y-1 pl-5">
            {vintage.gaps.map((gap) => (
              <li key={gap}>{gap}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {isForecast && Array.isArray(vintage?.next_updates) && vintage.next_updates.length > 0 ? (
        <p className="mt-3 text-sm leading-6 text-slate-600">
          <span className="font-semibold text-slate-800">Next updates: </span>
          {vintage.next_updates.map((u, i) => (
            <span key={u.source}>
              {i > 0 ? "; " : ""}
              <a href={u.url} target="_blank" rel="noreferrer" className="underline">
                {u.source}
              </a>{" "}
              ({formatSourceDate(u.due)})
            </span>
          ))}
          . This scenario will be refreshed when they land.
        </p>
      ) : null}
    </div>
  );
}
