/**
 * The forecast-based scenario on the Household impacts and Policy tabs, and
 * property tests for the arithmetic and formatting the tabs rely on.
 *
 * Separate from ScenariosTab.test.jsx so the baseline-callout contract there
 * stays independent of this change.
 */
import { fireEvent, render } from "@testing-library/react";
import fc from "fast-check";
import { describe, expect, it } from "vitest";

import MethodologyTab from "./MethodologyTab";
import PolicyTab from "./PolicyTab";
import ScenariosTab from "./ScenariosTab";
import data from "../../public/data/iran_impact_results.json";
import { formatCount, formatCurrency, formatSourceDate } from "../lib/formatters";
import { exampleHouseholdCost } from "../lib/householdCost";
import {
  getDefaultScenario,
  getScenarioGroups,
  getScenarioOptions,
} from "../lib/scenarioContent";

const forecast = data.scenarios.external_forecast;

function textOf(node) {
  return node.textContent.replace(/\s+/g, " ");
}

function button(container, startsWith) {
  return [...container.querySelectorAll("button")].find((b) =>
    b.textContent.startsWith(startsWith),
  );
}

describe("the Household impacts tab", () => {
  it("opens on the forecast-based scenario and shows its microsimulated figures", () => {
    const { container } = render(<ScenariosTab data={data} />);
    const text = textOf(container);
    expect(text).toContain(formatCurrency(forecast.summary.mean_net_impact));
    expect(text).toContain(`+${formatCount(forecast.summary.n_pushed_into_poverty)}`);
    expect(text).toContain("under the Latest forecasts scenario");
    expect(text).toContain("Forecast-based");
    expect(text).toContain("Cornwall Insight, price cap forecast");
  });

  it("groups the stress tests under their own label", () => {
    const { container } = render(<ScenariosTab data={data} />);
    const groups = [...container.querySelectorAll('[role="group"]')];
    expect(groups.map((g) => g.getAttribute("aria-label"))).toEqual([
      "Forecast-based",
      "Stress tests",
    ]);
    const labels = (group) => [...group.querySelectorAll("button")].map((b) => b.textContent);
    expect(labels(groups[0])).toHaveLength(1);
    expect(labels(groups[0])[0].startsWith("Latest forecasts (+")).toBe(true);
    const stress = labels(groups[1]);
    expect(stress).toHaveLength(3);
    ["Summer 2026 prices (+", "Sustained escalation (+", "Severe escalation (+"].forEach(
      (label, i) => expect(stress[i].startsWith(label), stress[i]).toBe(true),
    );
  });

  it("labels a stress test as one when it is selected, with its own citations", () => {
    const { container } = render(<ScenariosTab data={data} />);
    fireEvent.click(button(container, "Summer 2026 prices"));
    const text = textOf(container);
    expect(text).toContain("Stress test");
    expect(text).toContain("A stress test, not a forecast");
    expect(text).toContain("under the Summer 2026 prices stress test");
    expect(text).toContain(formatCurrency(data.scenarios.low_shock.summary.mean_net_impact));
    expect(text).toContain("Ofgem, price cap for July-September 2026");
  });

  it("shows the poverty count's range and what it rests on, for every scenario", () => {
    const { container } = render(<ScenariosTab data={data} />);
    for (const [key, startsWith] of [
      ["external_forecast", "Latest forecasts"],
      ["low_shock", "Summer 2026 prices"],
      ["central_shock", "Sustained escalation"],
      ["severe_shock", "Severe escalation"],
    ]) {
      fireEvent.click(button(container, startsWith));
      const scenario = data.scenarios[key];
      const combined = scenario.sensitivity.combined;
      const context = textOf(container.querySelector('[data-testid="poverty-count-context"]'));
      expect(context, key).toContain(
        `${formatCount(combined.n_newly_below_anchored_line_low)} to ${formatCount(combined.n_newly_below_anchored_line_high)}`,
      );
      expect(context, key).toContain(
        `${scenario.summary.n_records_newly_below_anchored_line.toLocaleString("en-GB")} survey records`,
      );
      expect(context, key).toContain(
        `${scenario.summary.largest_record_share_of_newly_below_pct}% of it`,
      );
    }
  });

  it("omits the poverty context rather than publish a partial one", () => {
    const cases = [
      ["sensitivity.combined.n_newly_below_anchored_line_low", undefined],
      ["sensitivity.combined.n_newly_below_anchored_line_high", NaN],
      // A range that does not contain the headline is a stale or mixed file.
      ["sensitivity.combined.n_newly_below_anchored_line_high", 1],
      ["summary.n_records_newly_below_anchored_line", 0],
      ["summary.n_records_newly_below_anchored_line", "754"],
      ["summary.largest_record_share_of_newly_below_pct", 140],
      ["summary.largest_record_share_of_newly_below_pct", undefined],
    ];
    for (const [path, value] of cases) {
      const broken = structuredClone(data);
      const parts = path.split(".");
      let node = broken.scenarios.external_forecast;
      for (const part of parts.slice(0, -1)) node = node[part];
      node[parts[parts.length - 1]] = value;
      const { container, unmount } = render(<ScenariosTab data={broken} />);
      expect(
        container.querySelector('[data-testid="poverty-count-context"]'),
        `${path}=${String(value)}`,
      ).toBeNull();
      expect(container.textContent).not.toContain("NaN");
      unmount();
    }
  });

  it("puts the forecast figures beside the stress tests in the comparison table", () => {
    const text = textOf(render(<ScenariosTab data={data} />).container);
    expect(text).toContain(
      `${formatCurrency(forecast.channel_decomposition.energy_shock)} (latest forecasts); stress tests:`,
    );
  });

  it("still opens on a stress test if a results file has no forecast scenario", () => {
    const older = structuredClone(data);
    delete older.scenarios.external_forecast;
    expect(getDefaultScenario(older)).toBe("low_shock");
    const text = textOf(render(<ScenariosTab data={older} />).container);
    expect(text).toContain("under the Summer 2026 prices stress test");
    expect(text).not.toContain("NaN");
  });
});

describe("the Policy options tab", () => {
  it("opens on the forecast-based scenario and labels it", () => {
    const text = textOf(render(<PolicyTab data={data} />).container);
    expect(text).toContain("Forecast-based");
    expect(text).toContain("Latest forecasts:");
  });
});

describe("the Methodology tab", () => {
  it("leads with the forecast scenario's figures and types every scenario", () => {
    const text = textOf(render(<MethodologyTab data={data} />).container);
    expect(text).toContain(
      `£${forecast.summary.mean_net_impact.toLocaleString("en-GB")}`,
    );
    expect(text).toContain(`£${forecast.summary.total_impact_bn}bn`);
    expect(text).toContain("Three scenarios are stress tests, not forecasts.");
    expect(text).toContain("one built from published forecasts");
    // The food row lists every scenario's figure, read from the data.
    for (const key of Object.keys(data.scenarios)) {
      expect(text).toContain(`${data.scenarios[key].params.food_increase_pct.toFixed(1)}%`);
    }
  });
});

describe("scenario metadata (property)", () => {
  it("lists every scenario exactly once, forecast first, each typed", () => {
    const keys = Object.keys(data.scenarios);
    fc.assert(
      fc.property(fc.subarray(keys, { minLength: 1 }), (subset) => {
        const partial = structuredClone(data);
        for (const key of keys) if (!subset.includes(key)) delete partial.scenarios[key];
        const options = getScenarioOptions(partial);
        expect(options.map((o) => o.id).sort()).toEqual([...subset].sort());
        for (const o of options) expect(["Forecast-based", "Stress test"]).toContain(o.typeLabel);
        const groups = getScenarioGroups(partial);
        expect(groups.flatMap((g) => g.options).length).toBe(subset.length);
        if (subset.includes("external_forecast")) {
          expect(options[0].id).toBe("external_forecast");
          expect(getDefaultScenario(partial)).toBe("external_forecast");
        }
      }),
    );
  });

  it("takes the type from the results file when it says", () => {
    const relabelled = structuredClone(data);
    relabelled.scenarios.low_shock.scenario_type = "annual forecast-based scenario";
    const option = getScenarioOptions(relabelled).find((o) => o.id === "low_shock");
    expect(option.typeLabel).toBe("Forecast-based");
  });
});

describe("the example household calculator (property)", () => {
  const price = fc.double({ min: 0, max: 300, noNaN: true });
  const spend = fc.double({ min: 0, max: 20_000, noNaN: true });
  const params = fc.record({
    cap_increase_pct: price,
    fuel_pct: price,
    food_increase_pct: price,
  });
  const spends = fc.record({ energyBill: spend, fuelSpend: spend, foodSpend: spend });

  it("never costs less when any price rises", () => {
    fc.assert(
      fc.property(
        params,
        spends,
        fc.constantFrom("cap_increase_pct", "fuel_pct", "food_increase_pct"),
        fc.double({ min: 0, max: 100, noNaN: true }),
        (p, s, key, delta) => {
          const before = exampleHouseholdCost(p, s);
          const after = exampleHouseholdCost({ ...p, [key]: p[key] + delta }, s);
          expect(after.total).toBeGreaterThanOrEqual(before.total);
        },
      ),
    );
  });

  it("never costs less when any spend rises, and the channels sum to the total", () => {
    fc.assert(
      fc.property(
        params,
        spends,
        fc.constantFrom("energyBill", "fuelSpend", "foodSpend"),
        fc.double({ min: 0, max: 5_000, noNaN: true }),
        (p, s, key, delta) => {
          const before = exampleHouseholdCost(p, s);
          const after = exampleHouseholdCost(p, { ...s, [key]: s[key] + delta });
          expect(after.total).toBeGreaterThanOrEqual(before.total);
          expect(before.energy + before.fuel + before.food).toBeCloseTo(before.total, 6);
        },
      ),
    );
  });

  it("matches the microsimulation's channel arithmetic for the forecast scenario", () => {
    // Same rule the pipeline applies: spend x rise. At the baseline mean
    // energy spend it gives the published energy channel to within rounding.
    const { energy } = exampleHouseholdCost(forecast.params, {
      energyBill: data.baseline.mean_energy_spend,
      fuelSpend: 0,
      foodSpend: 0,
    });
    expect(Math.abs(energy - forecast.channel_decomposition.energy_shock)).toBeLessThanOrEqual(1);
  });
});

describe("source dates (property)", () => {
  it("formats any ISO date without a time-zone shift", () => {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    fc.assert(
      fc.property(
        fc.integer({ min: 1900, max: 2100 }),
        fc.integer({ min: 1, max: 12 }),
        fc.integer({ min: 1, max: 28 }),
        (y, m, d) => {
          const iso = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
          expect(formatSourceDate(iso)).toBe(`${d} ${months[m - 1]} ${y}`);
          expect(formatSourceDate(iso.slice(0, 7))).toBe(`${months[m - 1]} ${y}`);
        },
      ),
    );
  });

  it("returns anything that is not an ISO date unchanged", () => {
    fc.assert(
      fc.property(
        fc.string().filter((s) => !/^\d{4}-\d{2}(-\d{2})?$/.test(s)),
        (s) => {
          expect(formatSourceDate(s)).toBe(s);
        },
      ),
    );
  });
});
