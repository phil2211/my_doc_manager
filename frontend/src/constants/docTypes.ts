export const DOC_TYPES = ["bill", "contract", "information", "commercial", "other"] as const;

export type DocType = (typeof DOC_TYPES)[number];

export function formatDocType(value: string | null | undefined): string {
  if (!value) return "—";
  return value.charAt(0).toUpperCase() + value.slice(1);
}
