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
