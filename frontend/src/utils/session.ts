const KEY = "smarttodo_session_id";

export function ensureSessionId(): string {
  let s = localStorage.getItem(KEY);
  if (!s) {
    s = crypto.randomUUID();
    localStorage.setItem(KEY, s);
  }
  return s;
}