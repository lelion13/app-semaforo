# Fix zona horaria cupo diario

## Problema

El cupo `max_rojos_dia` y `positivos_hoy` usaban medianoche UTC. En producción (2026-06-01) hubo 10 positivos en un día ART: 5 antes de las 21:00 ART y 5 entre 21:00–21:10 ART (ya día UTC 2026-06-02).

## Solución

- `zona_horaria` en `config.yaml` (default `America/Argentina/Buenos_Aires`).
- Override opcional: `APP_TIMEZONE`.
- Helper `utc_range_for_local_calendar_day` para consultas DB.
- Emails muestran hora en zona operativa.

## Despliegue

Solo backend: rebuild imagen + `docker compose pull && up -d backend`.
