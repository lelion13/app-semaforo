import { useEffect, useMemo, useRef, useState } from "react";
import { postRegistro } from "./api/client";
import { ErrorCamara } from "./components/ErrorCamara";
import { IdleScreen } from "./components/IdleScreen";
import { ResultadoRojo } from "./components/ResultadoRojo";
import { ResultadoVerde } from "./components/ResultadoVerde";
import { useCamera } from "./hooks/useCamera";
import { clearPendingRojo, getPendingRojo, savePendingRojo, useSorteo } from "./hooks/useSorteo";
import type { UiState } from "./types";

const EMPRESA_NOMBRE = (import.meta.env.VITE_EMPRESA_NOMBRE as string | undefined) || "Mi Empresa S.A.";
const LOGO_URL = (import.meta.env.VITE_EMPRESA_LOGO_URL as string | undefined) || "";

function Loading({ text }: { text: string }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-100 p-6">
      <div className="mb-5 h-16 w-16 animate-spin rounded-full border-4 border-slate-300 border-t-slate-700" />
      <p className="text-2xl font-semibold text-slate-800">{text}</p>
    </div>
  );
}

function Confirmado({ onFinalizar }: { onFinalizar: () => void }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-900 p-6 text-white">
      <p className="mb-8 max-w-2xl text-center text-3xl font-bold">
        Dirigite al laboratorio. El responsable ya fue notificado.
      </p>
      <button className="rounded-xl bg-blue-600 px-8 py-4 text-2xl font-bold" onClick={onFinalizar}>
        Finalizar
      </button>
    </div>
  );
}

export default function App() {
  const { cameraReady, cameraError, captureFrameBase64 } = useCamera();
  const { ejecutarSorteo, loading: sorteoLoading } = useSorteo();
  const [uiState, setUiState] = useState<UiState>("LOADING");
  const [sorteoId, setSorteoId] = useState<string | null>(null);
  const fotoRef = useRef<string | null>(null);

  useEffect(() => {
    if (cameraError) {
      setUiState("ERROR_CAMARA");
      return;
    }

    if (!cameraReady) {
      setUiState("LOADING");
      return;
    }

    const pending = getPendingRojo();
    if (pending) {
      setSorteoId(pending.sorteoId);
      setUiState("ROJO");
      return;
    }
    setUiState("IDLE");
  }, [cameraReady, cameraError]);

  useEffect(() => {
    if (uiState !== "VERDE") {
      return;
    }
    const timeout = window.setTimeout(() => setUiState("IDLE"), 5000);
    return () => window.clearTimeout(timeout);
  }, [uiState]);

  useEffect(() => {
    if (uiState !== "ROJO" || !sorteoId) {
      return;
    }
    try {
      fotoRef.current = captureFrameBase64();
    } catch {
      setUiState("ERROR_CAMARA");
    }
  }, [uiState, sorteoId, captureFrameBase64]);

  const startControl = async () => {
    if (!cameraReady || sorteoLoading) {
      return;
    }
    setUiState("LOADING");
    try {
      const response = await ejecutarSorteo();
      setSorteoId(response.sorteo_id);
      if (response.resultado === "verde") {
        setUiState("VERDE");
      } else {
        savePendingRojo(response.sorteo_id);
        setUiState("ROJO");
      }
    } catch {
      setUiState("IDLE");
    }
  };

  const handleRojoSubmit = async (data: { legajo: string; nombre: string; apellido: string }) => {
    if (!sorteoId || !fotoRef.current) {
      throw new Error("Sorteo pendiente incompleto");
    }
    setUiState("ENVIANDO");
    try {
      await postRegistro({
        sorteo_id: sorteoId,
        legajo: data.legajo,
        nombre: data.nombre,
        apellido: data.apellido,
        foto_base64: fotoRef.current
      });
      clearPendingRojo();
      setUiState("CONFIRMADO");
    } catch (_error) {
      setUiState("ROJO");
    }
  };

  const view = useMemo(() => {
    if (uiState === "ERROR_CAMARA") {
      return <ErrorCamara />;
    }
    if (uiState === "LOADING") {
      return <Loading text="Procesando sorteo..." />;
    }
    if (uiState === "IDLE") {
      return <IdleScreen empresaNombre={EMPRESA_NOMBRE} logoUrl={LOGO_URL} onStart={startControl} />;
    }
    if (uiState === "VERDE") {
      return <ResultadoVerde />;
    }
    if (uiState === "ROJO") {
      return <ResultadoRojo onSubmit={handleRojoSubmit} />;
    }
    if (uiState === "ENVIANDO") {
      return <Loading text="Procesando..." />;
    }
    return (
      <Confirmado
        onFinalizar={() => {
          setSorteoId(null);
          fotoRef.current = null;
          setUiState("IDLE");
        }}
      />
    );
  }, [uiState, startControl]);

  return view;
}
