import { v4 as uuidv4 } from "uuid";

const STORAGE_KEYS = {
  sessions: "mock_sessions",
  messages: "mock_messages",
};

function load(key, fallback) {
  try {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : fallback;
  } catch {
    return fallback;
  }
}

function save(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function getModels() {
  return [
    { id: "gpt-4o-mini", name: "GPT-4o mini (mock)" },
    { id: "claude-3.5", name: "Claude 3.5 (mock)" },
    { id: "local-llm", name: "Local LLM (mock)" },
  ];
}

export function getSessions() {
  const sessions = load(STORAGE_KEYS.sessions, []);
  return sessions.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

export function getSessionById(id) {
  return getSessions().find((s) => s.id === id);
}

export async function createSession({ model }) {
  const models = getModels();
  const modelInfo = models.find((m) => m.id === model);
  const session = {
    id: uuidv4(),
    title: "New Chat",
    model,
    modelName: modelInfo?.name || model,
    createdAt: new Date().toISOString(),
  };
  const sessions = getSessions();
  sessions.push(session);
  save(STORAGE_KEYS.sessions, sessions);
  // Initialize messages store
  const messages = load(STORAGE_KEYS.messages, {});
  messages[session.id] = [];
  save(STORAGE_KEYS.messages, messages);
  return session;
}

export function getMessages(sessionId) {
  const all = load(STORAGE_KEYS.messages, {});
  return all[sessionId] || [];
}

export async function sendMessage(sessionId, content) {
  const all = load(STORAGE_KEYS.messages, {});
  const sessions = getSessions();
  if (!all[sessionId]) all[sessionId] = [];

  const userMsg = {
    id: uuidv4(),
    role: "user",
    content,
    createdAt: new Date().toISOString(),
  };
  all[sessionId].push(userMsg);
  save(STORAGE_KEYS.messages, all);

  // Mock LLM response after a short delay
  await new Promise((res) => setTimeout(res, 400));
  const assistantMsg = {
    id: uuidv4(),
    role: "assistant",
    content: `Echo: ${content}`,
    createdAt: new Date().toISOString(),
  };
  all[sessionId].push(assistantMsg);
  save(STORAGE_KEYS.messages, all);

  // Update session title on first message
  const session = sessions.find((s) => s.id === sessionId);
  if (session && session.title === "New Chat") {
    session.title = content.slice(0, 20) || "New Chat";
    save(STORAGE_KEYS.sessions, sessions);
  }

  return all[sessionId];
}
