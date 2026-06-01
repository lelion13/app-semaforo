# Proposal: Ajustar probabilidad de sorteo

## Intent

Reducir la frecuencia de resultados `rojo` en operación real y pruebas en tablet, manteniendo el tope diario existente.

## Contexto

- Operación en producción mostró dos positivos consecutivos con legajo de prueba; estadísticamente posible con 30%, pero percibido como alto para el negocio.
- El cupo `max_rojos_dia` no evita rojos consecutivos; solo limita el total diario de registros completados.

## Cambio

| Parámetro | Antes | Después |
|-----------|-------|---------|
| `sorteo.probabilidad_rojo` | `30` | `10` |
| `sorteo.max_rojos_dia` | `5` | sin cambio |

Archivo: `backend/config.yaml` (embebido en imagen backend).

## Alcance

- Incluye: modificar config, rebuild/push backend GHCR, redeploy backend en VPS.
- Excluye: regla anti-consecutivos, cambios en frontend, cambios en lógica de `sorteo.py`.

## Rollback

Restaurar `probabilidad_rojo: 30` en `config.yaml`, rebuild backend, redeploy.

## Riesgos

- Menor tasa de controles aleatorios (~10% vs ~30%).
- Cambio requiere redeploy de **backend**; el frontend no se ve afectado.
