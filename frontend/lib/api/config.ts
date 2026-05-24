/** API base URL for browser fetch (Vercel + local). */

export function normalizeApiBase(raw: string): string {
  let base = raw.trim();
  while (base.endsWith("/")) {
    base = base.slice(0, -1);
  }
  if (base.endsWith("/api")) {
    base = base.slice(0, -4);
  }
  return base;
}

/** Railway URL in production; empty in local dev (uses Next.js rewrites). */
export const API_BASE = normalizeApiBase(
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "",
);

/** Build absolute or same-origin path for API calls. */
export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return API_BASE ? `${API_BASE}${normalized}` : normalized;
}

export function isProductionDeploy(): boolean {
  return (
    process.env.NEXT_PUBLIC_VERCEL_ENV === "production" ||
    process.env.NODE_ENV === "production"
  );
}

export function missingApiConfigMessage(): string | null {
  if (API_BASE) return null;
  if (typeof window === "undefined") return null;
  if (!isProductionDeploy()) return null;
  return (
    "API URL is not configured. In Vercel → Settings → Environment Variables, " +
    "set NEXT_PUBLIC_API_BASE_URL to your Railway backend URL (no trailing slash)."
  );
}
