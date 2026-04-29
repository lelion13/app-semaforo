export type UiState =
  | "ERROR_CAMARA"
  | "IDLE"
  | "LOADING"
  | "VERDE"
  | "ROJO"
  | "ENVIANDO"
  | "CONFIRMADO";

export type SorteoResultado = "verde" | "rojo";

export interface SorteoResponse {
  resultado: SorteoResultado;
  sorteo_id: string;
}

export interface RegistroPayload {
  sorteo_id: string;
  legajo: string;
  nombre: string;
  apellido: string;
  foto_base64: string;
}

export interface AuthUser {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  rol: "admin" | "rrhh";
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
}

export interface DashboardRegistro {
  id: string;
  sorteo_id: string;
  legajo: string;
  nombre: string;
  apellido: string;
  fecha_hora: string;
  email_enviado: boolean;
  email_intentos: number;
  email_error: string | null;
  estado_control: "pendiente" | "realizado" | "no_asistio";
  fecha_control: string | null;
  observacion_control: string | null;
}
