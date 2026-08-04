/**
 * Dashboard auth bootstrap.
 *
 * The dashboard has no login page, so we auto-provision a local demo account
 * on first load. The JWT is stored in localStorage under `auth_token`, which
 * the shared API client attaches to every request.
 */
import api from "./api";

const DEMO_EMAIL = "demo@example.com";
const DEMO_PASSWORD = "demo-password-123";

/**
 * Ensure a valid auth token exists, creating the demo account if needed.
 * Returns the token (or null if the API is unreachable).
 */
export async function ensureAuth(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  const existing = localStorage.getItem("auth_token");
  if (existing) return existing;

  try {
    // Account already exists from a previous run → just log in.
    const res = await api.post<{ access_token: string }>("/auth/login", {
      email: DEMO_EMAIL,
      password: DEMO_PASSWORD,
    });
    localStorage.setItem("auth_token", res.access_token);
    return res.access_token;
  } catch {
    try {
      const res = await api.post<{ access_token: string }>("/auth/register", {
        email: DEMO_EMAIL,
        username: "demo",
        password: DEMO_PASSWORD,
        full_name: "Demo User",
      });
      localStorage.setItem("auth_token", res.access_token);
      return res.access_token;
    } catch (e) {
      // Registration can 409 if another tab created the account concurrently —
      // fall back to logging in once before giving up.
      try {
        const res = await api.post<{ access_token: string }>("/auth/login", {
          email: DEMO_EMAIL,
          password: DEMO_PASSWORD,
        });
        localStorage.setItem("auth_token", res.access_token);
        return res.access_token;
      } catch (e2) {
        console.warn("Auto-auth unavailable (is the API running on :8000?)", e2);
        return null;
      }
    }
  }
}
