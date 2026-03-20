import { api } from "./api.js";

export async function loadCurrentUser() {
  try {
    return await api("/auth/me");
  } catch {
    return null;
  }
}

export function login(payload) {
  return api("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload) {
  return api("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logout() {
  try {
    await api("/auth/logout", { method: "POST" });
  } catch {
    // Ignore logout response errors and still clear client state.
  }
}
