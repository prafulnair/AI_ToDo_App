// src/utils/api.ts
import { getSessionId } from "./session";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const sessionId = getSessionId();

  const resp = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Session-Id": sessionId,
      ...(options.headers || {}),
    },
  });

  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${await resp.text()}`);
  }
  return resp.json();
}