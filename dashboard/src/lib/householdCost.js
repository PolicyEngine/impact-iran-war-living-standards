/**
 * The example household's extra annual cost under a scenario: each spend
 * times its scenario rise. The same arithmetic the microsimulation applies
 * to each household's own spending, kept here so the calculator and its
 * tests share one definition.
 */
export function exampleHouseholdCost(params, { energyBill, fuelSpend, foodSpend }) {
  const energy = energyBill * (params.cap_increase_pct / 100);
  const fuel = fuelSpend * (params.fuel_pct / 100);
  const food = foodSpend * (params.food_increase_pct / 100);
  return { energy, fuel, food, total: energy + fuel + food };
}
