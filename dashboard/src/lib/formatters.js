export function formatCurrency(value) {
  return `\u00A3${Math.round(Number(value)).toLocaleString("en-GB")}`;
}

export function formatBn(value) {
  return `\u00A3${Number(value).toFixed(1)}bn`;
}

export function formatPct(value, digits = 1) {
  return `${Number(value).toFixed(digits)}%`;
}

export function formatCount(value) {
  const num = Number(value);
  if (num >= 1e6) {
    return `${(num / 1e6).toFixed(1)}m`;
  }
  if (num >= 1e3) {
    return `${Math.round(num / 1e3).toLocaleString("en-GB")}k`;
  }
  return num.toLocaleString("en-GB");
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

/**
 * An ISO source date as a reader writes it: "2026-09-30" -> "30 Sep 2026",
 * "2026-11" -> "Nov 2026". Parsed by hand rather than through Date, which
 * reads a bare ISO date as UTC midnight and can render the previous day in
 * a western time zone. Anything else is returned unchanged, so a malformed
 * date shows as written rather than as "Invalid Date".
 */
export function formatSourceDate(iso) {
  if (typeof iso !== "string") return "";
  const match = /^(\d{4})-(\d{2})(?:-(\d{2}))?$/.exec(iso);
  if (!match) return iso;
  const [, year, month, day] = match;
  const name = MONTHS[Number(month) - 1];
  if (!name) return iso;
  return day ? `${Number(day)} ${name} ${year}` : `${name} ${year}`;
}
