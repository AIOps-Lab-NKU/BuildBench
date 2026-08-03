(function () {
  "use strict";

  const SESSION_HINT_KEY = "buildbench.session-hint.v1";
  let sessionPromise = null;

  function writeSessionHint(session) {
    const hint = session?.team
      ? { authenticated: true, team_name: String(session.team.name || "") }
      : { authenticated: false, team_name: "" };
    try {
      window.sessionStorage.setItem(SESSION_HINT_KEY, JSON.stringify(hint));
    } catch {
      // Storage may be unavailable in hardened or file:// previews.
    }
    return hint;
  }

  function getSessionHint() {
    try {
      const value = JSON.parse(window.sessionStorage.getItem(SESSION_HINT_KEY) || "null");
      if (!value || typeof value.authenticated !== "boolean") return null;
      return {
        authenticated: value.authenticated,
        team_name: typeof value.team_name === "string" ? value.team_name : "",
      };
    } catch {
      return null;
    }
  }

  async function readJson(response) {
    try {
      return await response.json();
    } catch {
      return {};
    }
  }

  async function request(path, options = {}) {
    const settings = {
      cache: "no-store",
      credentials: "same-origin",
      ...options,
      headers: new Headers(options.headers || {}),
    };
    const method = String(settings.method || "GET").toUpperCase();
    const publicAuthWrite =
      path === "/api/auth/register" || path === "/api/auth/login";
    if (!["GET", "HEAD", "OPTIONS"].includes(method) && !publicAuthWrite) {
      const session = await getSession();
      if (session?.csrf_token) settings.headers.set("X-CSRF-Token", session.csrf_token);
    }
    if (settings.json !== undefined) {
      settings.headers.set("Content-Type", "application/json");
      settings.body = JSON.stringify(settings.json);
      delete settings.json;
    }
    const response = await fetch(path, settings);
    const payload = await readJson(response);
    if (!response.ok) {
      const error = new Error(payload.error || `Request failed (${response.status})`);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function loadSession() {
    try {
      const response = await fetch("/api/auth/me", {
        cache: "no-store",
        credentials: "same-origin",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        writeSessionHint(null);
        return null;
      }
      const session = await readJson(response);
      writeSessionHint(session);
      return session;
    } catch {
      return null;
    }
  }

  function getSession(force = false) {
    if (force || !sessionPromise) sessionPromise = loadSession();
    return sessionPromise;
  }

  function clearSession() {
    sessionPromise = Promise.resolve(null);
    writeSessionHint(null);
  }

  function safeReturnUrl(fallback = "index.html") {
    const value = new URL(window.location.href).searchParams.get("return");
    if (!value) return fallback;
    try {
      const target = new URL(value, window.location.href);
      if (target.origin !== window.location.origin) return fallback;
      return `${target.pathname.split("/").pop() || fallback}${target.search}${target.hash}`;
    } catch {
      return fallback;
    }
  }

  async function requireSession() {
    const session = await getSession();
    if (session) return session;
    const current = `${window.location.pathname.split("/").pop() || "index.html"}${window.location.search}`;
    window.location.replace(`login.html?return=${encodeURIComponent(current)}`);
    return null;
  }

  async function logout() {
    await request("/api/auth/logout", { method: "POST" });
    clearSession();
  }

  window.BuildBenchAuth = Object.freeze({
    clearSession,
    getSessionHint,
    getSession,
    logout,
    request,
    requireSession,
    safeReturnUrl,
  });
})();
