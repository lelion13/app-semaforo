import type { RegistroPayload, SorteoResponse } from "../types";

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

export async function postSorteo(): Promise<SorteoResponse> {
  return request<SorteoResponse>("/api/sorteo", { method: "POST" });
}

export async function postRegistro(payload: RegistroPayload): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>("/api/registro", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
