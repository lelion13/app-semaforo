import type { DashboardRegistro, LoginResponse, RegistroPayload, SorteoResponse } from "../types";

const rawApiUrl = import.meta.env.VITE_API_URL as string | undefined;
const rawApiKey = import.meta.env.VITE_API_KEY as string | undefined;

if (!rawApiUrl) {
  throw new Error("Falta VITE_API_URL");
}
if (!rawApiKey) {
  throw new Error("Falta VITE_API_KEY");
}
if (!rawApiUrl.startsWith("https://") && !rawApiUrl.startsWith("http://localhost")) {
  throw new Error("VITE_API_URL debe usar HTTPS");
}
const API_URL = rawApiUrl;
const API_KEY = rawApiKey;
const AUTH_TOKEN_KEY = "dashboard_access_token";

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(init.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || "Error de comunicacion con el servidor");
  }
  return (await response.json()) as T;
}

async function requestNoApiKey<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {})
    }
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || "Error de comunicacion con el servidor");
  }
  return (await response.json()) as T;
}

async function requestWithAuth<T>(path: string, init: RequestInit): Promise<T> {
  const token = getDashboardToken();
  if (!token) {
    throw new Error("Sesion expirada");
  }
  return requestNoApiKey<T>(path, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(init.headers ?? {})
    }
  });
}

export async function postSorteo(): Promise<SorteoResponse> {
  return request<SorteoResponse>("/api/sorteo", { method: "POST" });
}

export async function postRegistro(payload: RegistroPayload): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>("/api/registro", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function saveDashboardToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function getDashboardToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function clearDashboardToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export async function getBootstrapStatus(): Promise<{ needs_bootstrap: boolean }> {
  return requestNoApiKey<{ needs_bootstrap: boolean }>("/api/auth/bootstrap-status", { method: "GET" });
}

export async function postBootstrapAdmin(payload: {
  nombre: string;
  apellido: string;
  email: string;
  password: string;
}): Promise<{ ok: boolean; message: string }> {
  return requestNoApiKey("/api/auth/bootstrap-admin", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function postLogin(payload: { email: string; password: string }): Promise<LoginResponse> {
  return requestNoApiKey<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function createDashboardUser(payload: {
  nombre: string;
  apellido: string;
  email: string;
  rol: "admin" | "rrhh";
}): Promise<{ ok: boolean; message: string }> {
  return requestWithAuth("/api/auth/users", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function requestPasswordReset(email: string): Promise<{ ok: boolean; message: string }> {
  return requestNoApiKey("/api/auth/request-password-reset", {
    method: "POST",
    body: JSON.stringify({ email })
  });
}

export async function confirmPassword(token: string, password: string): Promise<{ ok: boolean; message: string }> {
  return requestNoApiKey("/api/auth/confirm-password", {
    method: "POST",
    body: JSON.stringify({ token, password })
  });
}

export async function getDashboardRegistros(): Promise<DashboardRegistro[]> {
  return requestWithAuth<DashboardRegistro[]>("/api/dashboard/registros", { method: "GET" });
}

export async function patchDashboardRegistro(
  id: string,
  payload: { estado_control: "pendiente" | "realizado" | "no_asistio"; observacion_control?: string | null }
): Promise<DashboardRegistro> {
  return requestWithAuth<DashboardRegistro>(`/api/dashboard/registros/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}
