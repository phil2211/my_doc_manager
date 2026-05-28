/** Format ISO datetime for HTML date input (YYYY-MM-DD, local calendar). */
export function toDateInputValue(iso: string | null | undefined): string {
  if (!iso) return "";
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return "";
  const year = parsed.getFullYear();
  const month = String(parsed.getMonth() + 1).padStart(2, "0");
  const day = String(parsed.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Convert date input value to ISO date string for API (YYYY-MM-DD). */
export function dateInputToApiValue(value: string): string | null {
  if (!value) return null;
  return value;
}
