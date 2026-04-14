/**
 * Design tokens — inlined from @policyengine/design-system/tokens/colors
 * to avoid ESM bundling issues with Next.js.
 *
 * Palette: grays + dark green/teal only.
 */
export const colors = {
  primary: {
    50: "#E6FFFA",
    100: "#B2F5EA",
    200: "#81E6D9",
    300: "#4FD1C5",
    400: "#38B2AC",
    500: "#319795",
    600: "#2C7A7B",
    700: "#285E61",
    800: "#234E52",
    900: "#1D4044",
  },
  gray: {
    50: "#F9FAFB",
    100: "#F2F4F7",
    200: "#E2E8F0",
    300: "#D1D5DB",
    400: "#9CA3AF",
    500: "#6B7280",
    600: "#4B5563",
    700: "#344054",
    800: "#1F2937",
    900: "#101828",
  },
  border: {
    light: "#E2E8F0",
    medium: "#CBD5E1",
    dark: "#94A3B8",
  },
};

// Transmission channel colors — varying shades of teal/green + grays
export const channelColors = {
  energy: "#1D4044",        // primary-900
  fuel: "#285E61",          // primary-700
  food: "#2C7A7B",          // primary-600
  benefit_erosion: "#9CA3AF", // gray-400
  fiscal_drag: "#D1D5DB",   // gray-300
};

// Policy colors — alternating teal shades and grays for distinction
export const policyColors = {
  epg: "#1D4044",              // primary-900
  flat_rebate: "#285E61",      // primary-700
  ct_rebate: "#2C7A7B",        // primary-600
  uc_uplift: "#38B2AC",        // primary-400
  fuel_duty_cut: "#6B7280",    // gray-500
  means_tested: "#4B5563",     // gray-600
  accelerated_uprating: "#9CA3AF", // gray-400
  social_tariff: "#319795",       // primary-500
  combined: "#1D4044",         // primary-900
};

// Quintile colors — darkest for poorest, lightest for richest
export const quintileColors = {
  "Q1 (poorest)": "#1D4044",   // primary-900
  "Q2": "#285E61",             // primary-700
  "Q3": "#2C7A7B",            // primary-600
  "Q4": "#9CA3AF",            // gray-400
  "Q5 (richest)": "#D1D5DB",  // gray-300
};
