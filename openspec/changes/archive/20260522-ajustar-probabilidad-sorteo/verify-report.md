# Verify report: Ajustar probabilidad de sorteo

**Fecha:** 2026-05-22  
**Estado:** Verificado en producción

## Criterios

| Criterio | Resultado |
|----------|-----------|
| `config.yaml` con `probabilidad_rojo: 10` | OK |
| Backend GHCR publicado tras push | OK |
| Registros rojos persistidos con email `ok` | OK (dashboard VPS) |
| Kiosk operativo post-deploy | OK |

## Notas

- El job de frontend en el mismo push puede fallar por causa independiente (deps dashboard); no bloquea el cambio de probabilidad.
- Dos rojos consecutivos con 10% tienen probabilidad ~1% por par independiente; no implica bug de persistencia.
