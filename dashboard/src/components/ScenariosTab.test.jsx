/**
 * Render-level contract for the scenario baseline callout.
 *
 * #54 review A2: optional chaining stops an exception but still publishes
 * "£ on…" or "NaNp a litre" when a field is missing. The block is now
 * omitted unless every field is present, and these tests hold that.
 *
 * A render test would also have caught the bug in this PR's first version,
 * where `preConflict` was declared in one component and used in another:
 * lint and build both passed on an out-of-scope identifier.
 */
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ScenariosTab from "./ScenariosTab";
import data from "../../public/data/iran_impact_results.json";

const preConflict = data.metadata.pre_conflict_baseline;

function textOf(withData) {
  const { container } = render(<ScenariosTab data={withData} />);
  return container.textContent.replace(/\s+/g, " ");
}

describe("scenario baseline callout", () => {
  it("states both reference periods and the application year", () => {
    const text = textOf(data);
    expect(text).toContain("April–June 2026");
    expect(text).toContain(preConflict.pump_price_period);
    expect(text).toContain(`${data.year}-${String(data.year + 1).slice(2)}`);
  });

  it("attributes the published cap to Ofgem and the inferred one to us", () => {
    const text = textOf(data);
    // #54 review A1: £1,641 is Ofgem's published April–June figure; the
    // new-basis figure is this study's inference.
    expect(text).toContain(
      `£${preConflict.energy_price_cap_old_basis_gbp.toLocaleString("en-GB")}`,
    );
    expect(text).toContain("inferred by this study");
    expect(text).toContain("No cap value enters the calculation");
  });

  it("renders the observed pump anchors, rounded", () => {
    const text = textOf(data);
    expect(text).toContain(`${Math.round(preConflict.petrol_pence_per_litre)}p`);
    expect(text).toContain(`${Math.round(preConflict.diesel_pence_per_litre)}p`);
  });

  it("omits the callout rather than publishing a blank or NaN", () => {
    const missing = structuredClone(data);
    delete missing.metadata.pre_conflict_baseline.petrol_pence_per_litre;
    const text = textOf(missing);
    expect(text).not.toContain("NaN");
    expect(text).not.toContain("What the percentages are measured from");
  });

  it("omits the callout when a field is explicitly null", () => {
    const nulled = structuredClone(data);
    nulled.metadata.pre_conflict_baseline.pump_price_period = null;
    const text = textOf(nulled);
    expect(text).not.toContain("What the percentages are measured from");
  });

  it("omits the callout for present but invalid values", () => {
    // Presence checks let "£oops", "NaNp a litre" and "2027-271" publish
    // (#54 re-review A2). Each of these is present and non-null.
    const invalid = [
      ["metadata.pre_conflict_baseline.petrol_pence_per_litre", "oops"],
      ["metadata.pre_conflict_baseline.energy_price_cap_old_basis_gbp", "1641"],
      ["metadata.pre_conflict_baseline.diesel_pence_per_litre", 0],
      ["metadata.pre_conflict_baseline.energy_price_cap_new_basis_gbp", -5],
      ["metadata.pre_conflict_baseline.petrol_pence_per_litre", NaN],
      ["metadata.pre_conflict_baseline.pump_price_period", "   "],
      ["year", "2027"],
      ["year", 2027.5],
      ["year", 0],
      ["year", -1],
      ["year", 99],
      ["year", 999],
      ["year", 10000],
    ];

    for (const [path, value] of invalid) {
      const broken = structuredClone(data);
      const parts = path.split(".");
      let node = broken;
      for (const part of parts.slice(0, -1)) node = node[part];
      node[parts[parts.length - 1]] = value;

      const text = textOf(broken);
      expect(text, `${path}=${String(value)} still rendered the callout`)
        .not.toContain("What the percentages are measured from");
      expect(text).not.toContain("NaN");
    }
  });

  it("follows the data rather than hard-coding the anchors", () => {
    const moved = structuredClone(data);
    moved.metadata.pre_conflict_baseline.petrol_pence_per_litre = 200.4;
    moved.metadata.pre_conflict_baseline.energy_price_cap_old_basis_gbp = 9999;
    const text = textOf(moved);
    expect(text).toContain("200p");
    expect(text).toContain("£9,999");
  });
});
