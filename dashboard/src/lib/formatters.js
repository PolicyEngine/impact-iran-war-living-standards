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
