/**
 * Render-level contract for the methodology tab's headline figures.
 *
 * Renders the component with the committed results file and asserts the
 * user-visible text. This is what #53 review A2 asked for. An earlier
 * attempt parsed the source for `data.…` paths instead; mutation testing
 * showed it accepted seven display-breaking changes — a wrong-but-valid key,
 * an out-of-range quintile index, a hard-coded literal — while failing on a
 * comment. Asserting rendered output is the only thing that closes it.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MethodologyTab from "./MethodologyTab";
import data from "../../public/data/iran_impact_results.json";

// The contract, derived from the committed data rather than hard-coded, so
// a deliberate results change updates it and an accidental binding change
// does not.
const central = data.scenarios.central_shock;
const sensitivity = central.sensitivity.combined;
const ratioOfMeans = Math.round(
  central.by_quintile[0].mean_impact /
    data.baseline.by_quintile[0].mean_net_income /
    (central.by_quintile[4].mean_impact /
      data.baseline.by_quintile[4].mean_net_income),
);

function renderTab() {
  const { container } = render(<MethodologyTab data={data} />);
  return container.textContent.replace(/\s+/g, " ");
}

describe("MethodologyTab headline figures", () => {
  it("renders the household count from the data", () => {
    expect(renderTab()).toContain(`${data.baseline.n_households_m}m households`);
  });

  it("renders the central cost per household and total", () => {
    const text = renderTab();
    expect(text).toContain(
      `£${central.summary.mean_net_impact.toLocaleString("en-GB")}`,
    );
    expect(text).toContain(`£${central.summary.total_impact_bn}bn`);
  });

  it("renders the regressivity ratio on the ratio-of-means basis", () => {
    expect(renderTab()).toContain(`${ratioOfMeans}×`);
  });

  it("renders the total range as a complete ordered phrase", () => {
    // Asserting each endpoint separately lets a low/high swap pass, because
    // both still appear somewhere in the text (#53 re-review A2).
    expect(renderTab()).toContain(
      `£${sensitivity.total_impact_bn_low}bn to £${sensitivity.total_impact_bn_high}bn`,
    );
  });

  it("renders the uprating shortfall range as a complete ordered phrase", () => {
    expect(renderTab()).toContain(
      `£${sensitivity.uprating_shortfall_bn_low}bn–£${sensitivity.uprating_shortfall_bn_high}bn`,
    );
  });

  it("does not claim fuel and food use household-level spending", () => {
    const text = renderTab();
    // #53 review A1: only energy is household-specific.
    expect(text).toContain("gross-income decile");
    expect(text).not.toContain(
      "Three price channels applied to each household's own modelled spending",
    );
  });

  it("moves every headline input independently, so no literal survives", () => {
    // A literal equal to today's value renders identically, so each input is
    // moved and the OLD phrase must disappear. The previous version moved
    // only four of them, leaving the ratio operands, the total-range high
    // endpoint and the shortfall low endpoint unguarded (#53 re-review A2).
    const cases = [
      ["baseline.n_households_m", 99.9, `${data.baseline.n_households_m}m households`],
      [
        "scenarios.central_shock.summary.mean_net_impact",
        4321,
        `£${central.summary.mean_net_impact.toLocaleString("en-GB")}`,
      ],
      [
        "scenarios.central_shock.summary.total_impact_bn",
        99.9,
        `£${central.summary.total_impact_bn}bn`,
      ],
      [
        "scenarios.central_shock.sensitivity.combined.total_impact_bn_low",
        11.1,
        `£${sensitivity.total_impact_bn_low}bn to`,
      ],
      [
        "scenarios.central_shock.sensitivity.combined.total_impact_bn_high",
        77.7,
        `to £${sensitivity.total_impact_bn_high}bn`,
      ],
      [
        "scenarios.central_shock.sensitivity.combined.uprating_shortfall_bn_low",
        1.11,
        `£${sensitivity.uprating_shortfall_bn_low}bn–`,
      ],
      [
        "scenarios.central_shock.sensitivity.combined.uprating_shortfall_bn_high",
        8.88,
        `–£${sensitivity.uprating_shortfall_bn_high}bn`,
      ],
      // ALL FOUR operands of the regressivity ratio, one at a time. Moving
      // only two let a formula with the other two hard-coded still pass
      // (#53 re-review A2).
      ["scenarios.central_shock.by_quintile.0.mean_impact", 50, `${ratioOfMeans}×`],
      ["baseline.by_quintile.0.mean_net_income", 250000, `${ratioOfMeans}×`],
      ["scenarios.central_shock.by_quintile.4.mean_impact", 90000, `${ratioOfMeans}×`],
      ["baseline.by_quintile.4.mean_net_income", 20000, `${ratioOfMeans}×`],
    ];

    for (const [path, value, oldPhrase] of cases) {
      const moved = structuredClone(data);
      const parts = path.split(".");
      let node = moved;
      for (const part of parts.slice(0, -1)) node = node[part];
      node[parts[parts.length - 1]] = value;

      const { container } = render(<MethodologyTab data={moved} />);
      const text = container.textContent.replace(/\s+/g, " ");
      expect(text, `${path} appears to be hard-coded`).not.toContain(oldPhrase);
    }
  });
});
