import { useEffect, useMemo, useRef, useState } from "react";
import {
  clearDashboardToken,
  confirmPassword,
  createDashboardUser,
  getBootstrapStatus,
  getDashboardRegistros,
  getDashboardRegistroPhotoUrl,
  getDashboardToken,
  patchDashboardRegistro,
  postBootstrapAdmin,
  postLogin,
  postRegistro,
  requestPasswordReset,
  saveDashboardToken
} from "./api/client";
import { ErrorCamara } from "./components/ErrorCamara";
import { IdleScreen } from "./components/IdleScreen";
import { ResultadoRojo } from "./components/ResultadoRojo";
import { ResultadoVerde } from "./components/ResultadoVerde";
import { useCamera } from "./hooks/useCamera";
import { clearPendingRojo, getPendingRojo, savePendingRojo, useSorteo } from "./hooks/useSorteo";
import type { DashboardRegistro, UiState } from "./types";

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

function KioskApp() {
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

function SetupPage() {
  const [loading, setLoading] = useState(true);
  const [needsBootstrap, setNeedsBootstrap] = useState(false);
  const [message, setMessage] = useState("");
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resetEmail, setResetEmail] = useState("");
  const token = new URLSearchParams(window.location.search).get("token");

  useEffect(() => {
    if (token) {
      setLoading(false);
      return;
    }
    getBootstrapStatus()
      .then((data) => setNeedsBootstrap(data.needs_bootstrap))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <Loading text="Cargando..." />;

  if (token) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-3 p-6">
        <h1 className="text-2xl font-bold">Definir contrasena</h1>
        {message && <p className="text-sm text-slate-700">{message}</p>}
        <input className="rounded border p-2" type="password" placeholder="Nueva clave" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button
          className="rounded bg-slate-900 p-2 text-white"
          onClick={async () => {
            if (password.length < 10) {
              setMessage("La clave debe tener al menos 10 caracteres.");
              return;
            }
            try {
              await confirmPassword(token, password);
              setMessage("Clave actualizada. Ya podes iniciar sesion.");
            } catch (error) {
              const messageText = error instanceof Error ? error.message : "";
              if (messageText.includes("at least 10 characters")) {
                setMessage("La clave debe tener al menos 10 caracteres.");
              } else if (messageText.includes("Token invalido o expirado")) {
                setMessage("El enlace es invalido o expiro. Solicita uno nuevo.");
              } else {
                setMessage("No se pudo actualizar la clave.");
              }
            }
          }}
        >
          Guardar clave
        </button>
      </div>
    );
  }

  if (needsBootstrap) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-3 p-6">
        <h1 className="text-2xl font-bold">Crear primer admin</h1>
        {message && <p className="text-sm text-slate-700">{message}</p>}
        <input className="rounded border p-2" placeholder="Nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} />
        <input className="rounded border p-2" placeholder="Apellido" value={apellido} onChange={(e) => setApellido(e.target.value)} />
        <input className="rounded border p-2" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="rounded border p-2" type="password" placeholder="Clave" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button
          className="rounded bg-slate-900 p-2 text-white"
          onClick={async () => {
            try {
              await postBootstrapAdmin({ nombre, apellido, email, password });
              setMessage("Admin creado. Ya podes usar /dashboard");
              setNeedsBootstrap(false);
            } catch {
              setMessage("No se pudo crear el admin.");
            }
          }}
        >
          Crear admin
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-3 p-6">
      <h1 className="text-2xl font-bold">Gestion de acceso</h1>
      {message && <p className="text-sm text-slate-700">{message}</p>}
      <p className="text-sm text-slate-600">Bootstrap finalizado. Podes solicitar recuperacion de clave.</p>
      <input className="rounded border p-2" placeholder="Email" value={resetEmail} onChange={(e) => setResetEmail(e.target.value)} />
      <button
        className="rounded bg-slate-900 p-2 text-white"
        onClick={async () => {
          try {
            await requestPasswordReset(resetEmail);
            setMessage("Si el usuario existe, recibira un email.");
          } catch {
            setMessage("No se pudo solicitar reset.");
          }
        }}
      >
        Enviar enlace
      </button>
    </div>
  );
}

function DashboardPage() {
  const [token, setToken] = useState<string | null>(getDashboardToken());
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [registros, setRegistros] = useState<DashboardRegistro[]>([]);
  const [newUser, setNewUser] = useState({ nombre: "", apellido: "", email: "", rol: "rrhh" as "admin" | "rrhh" });
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [photoLoading, setPhotoLoading] = useState(false);

  const load = async () => {
    try {
      const data = await getDashboardRegistros();
      setRegistros(data);
    } catch {
      setMessage("Sesion vencida o error de carga");
      clearDashboardToken();
      setToken(null);
    }
  };

  useEffect(() => {
    if (token) {
      void load();
    }
  }, [token]);

  if (!token) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-3 p-6">
        <h1 className="text-2xl font-bold">Login dashboard</h1>
        {message && <p className="text-sm text-slate-700">{message}</p>}
        <input className="rounded border p-2" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="rounded border p-2" type="password" placeholder="Clave" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button
          className="rounded bg-slate-900 p-2 text-white"
          onClick={async () => {
            try {
              const auth = await postLogin({ email, password });
              saveDashboardToken(auth.access_token);
              setToken(auth.access_token);
            } catch {
              setMessage("Credenciales invalidas.");
            }
          }}
        >
          Ingresar
        </button>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <h1 className="text-2xl font-bold">Dashboard RRHH</h1>
        <button className="rounded border px-3 py-1" onClick={() => void load()}>
          Refrescar
        </button>
        <button
          className="rounded border px-3 py-1"
          onClick={() => {
            clearDashboardToken();
            setToken(null);
          }}
        >
          Salir
        </button>
      </div>
      {message && <p className="mb-2 text-sm text-slate-700">{message}</p>}

      <div className="mb-4 grid gap-2 rounded border p-3 md:max-w-3xl md:grid-cols-5">
        <input className="rounded border p-2" placeholder="Nombre" value={newUser.nombre} onChange={(e) => setNewUser((p) => ({ ...p, nombre: e.target.value }))} />
        <input className="rounded border p-2" placeholder="Apellido" value={newUser.apellido} onChange={(e) => setNewUser((p) => ({ ...p, apellido: e.target.value }))} />
        <input className="rounded border p-2" placeholder="Email" value={newUser.email} onChange={(e) => setNewUser((p) => ({ ...p, email: e.target.value }))} />
        <select className="rounded border p-2" value={newUser.rol} onChange={(e) => setNewUser((p) => ({ ...p, rol: e.target.value as "admin" | "rrhh" }))}>
          <option value="rrhh">rrhh</option>
          <option value="admin">admin</option>
        </select>
        <button
          className="rounded bg-slate-900 p-2 text-white"
          onClick={async () => {
            try {
              await createDashboardUser(newUser);
              setMessage("Usuario creado. Se envio enlace por email.");
            } catch {
              setMessage("No se pudo crear usuario.");
            }
          }}
        >
          Crear usuario
        </button>
      </div>

      <div className="overflow-auto rounded border">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-2">Fecha</th>
              <th className="p-2">Legajo</th>
              <th className="p-2">Nombre</th>
              <th className="p-2">Estado</th>
              <th className="p-2">Email</th>
              <th className="p-2">Accion</th>
              <th className="p-2">Foto</th>
            </tr>
          </thead>
          <tbody>
            {registros.map((item) => (
              <tr key={item.id} className="border-t">
                <td className="p-2">{new Date(item.fecha_hora).toLocaleString()}</td>
                <td className="p-2">{item.legajo}</td>
                <td className="p-2">
                  {item.nombre} {item.apellido}
                </td>
                <td className="p-2">{item.estado_control}</td>
                <td className="p-2">{item.email_enviado ? "ok" : "fallo"}</td>
                <td className="p-2">
                  <select
                    className="rounded border p-1"
                    value={item.estado_control}
                    onChange={async (e) => {
                      const estado = e.target.value as "pendiente" | "realizado" | "no_asistio";
                      await patchDashboardRegistro(item.id, { estado_control: estado });
                      await load();
                    }}
                  >
                    <option value="pendiente">pendiente</option>
                    <option value="realizado">realizado</option>
                    <option value="no_asistio">no_asistio</option>
                  </select>
                </td>
                <td className="p-2">
                  <button
                    className="rounded border px-2 py-1"
                    onClick={async () => {
                      setPhotoLoading(true);
                      try {
                        const url = await getDashboardRegistroPhotoUrl(item.id);
                        setPhotoUrl((prev) => {
                          if (prev) URL.revokeObjectURL(prev);
                          return url;
                        });
                      } catch {
                        setMessage("No se pudo cargar la foto.");
                      } finally {
                        setPhotoLoading(false);
                      }
                    }}
                  >
                    Ver foto
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {(photoLoading || photoUrl) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="max-h-[95vh] w-full max-w-3xl rounded bg-white p-3">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Foto del evento</h2>
              <button
                className="rounded border px-2 py-1"
                onClick={() => {
                  if (photoUrl) URL.revokeObjectURL(photoUrl);
                  setPhotoUrl(null);
                  setPhotoLoading(false);
                }}
              >
                Cerrar
              </button>
            </div>
            <div className="flex min-h-[200px] items-center justify-center">
              {photoLoading && <p className="text-sm text-slate-700">Cargando foto...</p>}
              {!photoLoading && photoUrl && <img src={photoUrl} alt="Registro positivo" className="max-h-[80vh] w-auto rounded" />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const path = window.location.pathname;
  if (path.startsWith("/dashboard")) {
    return <DashboardPage />;
  }
  if (path.startsWith("/user")) {
    return <SetupPage />;
  }
  return <KioskApp />;
}
