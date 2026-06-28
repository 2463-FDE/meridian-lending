export const GATEWAY_URL =
  process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000";

// ---- auth/session helpers (browser-only localStorage) --------------------

export interface SessionUser {
  id: string | number;
  username: string;
  role: "borrower" | "csr" | "underwriter" | "admin" | string;
  name: string;
}

const TOKEN_KEY = "meridian.token";
const USER_KEY = "meridian.user";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getUser(): SessionUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionUser;
  } catch {
    return null;
  }
}

export function setSession(token: string, user: SessionUser) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

// ---- fetch helpers -------------------------------------------------------

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail || `Request failed (${status})`);
    this.status = status;
    this.detail = detail;
  }
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parse(res: Response) {
  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : typeof data === "string" && data
          ? data
          : `Request failed (${res.status})`;
    throw new ApiError(res.status, detail);
  }
  return data;
}

export async function apiGet(path: string) {
  const res = await fetch(`${GATEWAY_URL}${path}`, {
    cache: "no-store",
    headers: { ...authHeaders() },
  });
  return parse(res);
}

export async function apiPost(path: string, body?: unknown) {
  const res = await fetch(`${GATEWAY_URL}${path}`, {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return parse(res);
}

export async function apiDelete(path: string) {
  const res = await fetch(`${GATEWAY_URL}${path}`, {
    method: "DELETE",
    cache: "no-store",
    headers: { ...authHeaders() },
  });
  return parse(res);
}
