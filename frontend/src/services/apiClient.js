// Backend API client bridging to the Django minimal chat API.
// Endpoints expected (per backend_progress.md):
// - GET /api/llms/
// - POST /api/sessions/ { llm: number, title?: string }
// - GET /api/sessions/ (optional)
// - GET /api/sessions/{uuid}/messages
// - POST /api/sessions/{uuid}/chat { message: string, options?: object }

import * as mock from "./mockApi.js";

const BASE = import.meta.env.VITE_API_BASE_URL || "/api";
const USE_FALLBACK = true; // fallback to mock when backend not available

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return undefined;
}

async function ensureCsrf() {
  let token = getCookie("csrftoken");
  if (!token) {
    // Issue a token; cookie will be set by server
    try {
      await fetch(`${BASE}/csrf/`, { credentials: "include" });
    } catch {
      // ignore; will retry using mock fallback if needed
    }
    token = getCookie("csrftoken");
  }
  return token;
}

async function http(path, opts = {}) {
  const url = `${BASE}${path}`;
  const method = (opts.method || "GET").toUpperCase();
  const headers = {
    "Content-Type": "application/json",
    ...(opts.headers || {}),
  };
  // Add CSRF header for unsafe methods
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const token = await ensureCsrf();
    if (token) headers["X-CSRFToken"] = token;
  }
  const res = await fetch(url, {
    method,
    headers,
    credentials: "include",
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    const err = new Error(`HTTP ${res.status}: ${text || res.statusText}`);
    err.status = res.status;
    throw err;
  }
  // Try JSON, allow empty
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return null;
}

export async function getLLMs() {
  // Expect list like: [{ id, name, provider, model, is_active }]
  try {
    return await http("/llms/");
  } catch (e) {
    if (!USE_FALLBACK) throw e;
    // Map mock models to LLM list shape
    const models = mock.getModels();
    return models.map((m, idx) => ({
      id: idx + 1,
      name: m.name,
      provider: "MOCK",
      model: m.id,
      is_active: true,
    }));
  }
}

export async function createSession({ llm, title }) {
  // Backend expects { llm: number, title?: string }
  try {
    return await http("/sessions/", { method: "POST", body: { llm, title } });
  } catch (e) {
    if (!USE_FALLBACK) throw e;
    // Use mock: choose model by llm index
    const mockModels = mock.getModels();
    const model = mockModels[(llm - 1) % mockModels.length]?.id || "local-llm";
    const s = await mock.createSession({ model });
    // Return shape similar to backend
    return { uuid: s.id, title: s.title };
  }
}

export async function listSessions() {
  // Optional; backend may require auth. Handle 401/403 gracefully.
  try {
    return await http("/sessions/");
  } catch (e) {
    if (USE_FALLBACK) {
      // Map mock sessions to backend-like shape
      return mock.getSessions().map((s) => ({ uuid: s.id, title: s.title }));
    }
    if (e.status === 401 || e.status === 403 || e.status === 404) return [];
    throw e;
  }
}

export async function getMessages(sessionUuid) {
  try {
    return await http(`/sessions/${sessionUuid}/messages/`);
  } catch (e) {
    if (!USE_FALLBACK) throw e;
    const ms = mock.getMessages(sessionUuid);
    return ms.map((m) => ({
      id: m.id,
      role: m.role,
      content: m.content,
      created_at: m.createdAt,
    }));
  }
}

export async function sendMessage(sessionUuid, message, options) {
  try {
    return await http(`/sessions/${sessionUuid}/chat/`, {
      method: "POST",
      body: { message, options },
    });
  } catch (e) {
    if (!USE_FALLBACK) throw e;
    const ms = await mock.sendMessage(sessionUuid, message);
    const last = ms[ms.length - 1];
    return {
      session_uuid: sessionUuid,
      assistant_message: {
        id: last.id,
        role: last.role,
        content: last.content,
      },
      usage: {},
    };
  }
}
