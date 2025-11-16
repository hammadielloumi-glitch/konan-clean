import { API_BASE_URL } from "src/config/api";

async function request(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });

    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const body = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const detail = isJson ? body?.detail || JSON.stringify(body) : body;
      throw new Error(detail || "Erreur inattendue");
    }

    return body;
  } catch (error) {
    throw new Error(error?.message || "Impossible de contacter le serveur");
  }
}

export async function login(email, password) {
  const trimmedEmail = email?.trim();
  const trimmedPassword = password?.trim();
  if (!trimmedEmail || !trimmedPassword) {
    throw new Error("Identifiants requis");
  }
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email: trimmedEmail, password: trimmedPassword }),
  });
}

export async function register(email, password) {
  const trimmedEmail = email?.trim();
  const trimmedPassword = password?.trim();
  if (!trimmedEmail || !trimmedPassword) {
    throw new Error("Email et mot de passe requis");
  }
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email: trimmedEmail, password: trimmedPassword }),
  });
}
