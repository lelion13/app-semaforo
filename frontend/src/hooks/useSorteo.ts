import { useEffect, useState } from "react";
import { postSorteo } from "../api/client";
import type { SorteoResponse } from "../types";

const SESSION_KEY = "control_rojo_pendiente";

interface PendingState {
  sorteoId: string;
  estado: "rojo_pendiente";
}

export function getPendingRojo(): PendingState | null {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as PendingState;
    if (parsed.sorteoId && parsed.estado === "rojo_pendiente") {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

export function savePendingRojo(sorteoId: string): void {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ sorteoId, estado: "rojo_pendiente" }));
}

export function clearPendingRojo(): void {
  sessionStorage.removeItem(SESSION_KEY);
}

export function useSorteo() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const pending = getPendingRojo();
    if (!pending) {
      clearPendingRojo();
    }
  }, []);

  const ejecutarSorteo = async (): Promise<SorteoResponse> => {
    setLoading(true);
    setError(null);
    try {
      return await postSorteo();
    } catch (_e) {
      setError("No se pudo realizar el sorteo. Intenta nuevamente.");
      throw _e;
    } finally {
      setLoading(false);
    }
  };

  return { ejecutarSorteo, loading, error };
}
