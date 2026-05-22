# SDD — app-semaforo

Este proyecto usa **Spec-Driven Development (OpenSpec)**. Las especificaciones en `openspec/specs/` describen el comportamiento **actual** acordado del sistema. Los cambios futuros se documentan en `openspec/changes/{nombre-cambio}/` antes de implementarse.

## Estructura

```
openspec/
├── config.yaml          # Contexto del proyecto y reglas SDD
├── specs/               # Fuente de verdad (comportamiento vigente)
│   ├── sorteo/
│   ├── kiosk-ui/
│   ├── registro/
│   ├── email/
│   ├── auth-dashboard/
│   └── deploy/
└── changes/             # Cambios activos (vacío hasta el primer change)
    └── archive/         # Cambios completados (audit trail)
```

## Flujo recomendado para un cambio

1. **Explorar** — aclarar alcance y riesgos (`sdd-explore`).
2. **Proponer** — `openspec/changes/{change}/proposal.md` (`sdd-propose`).
3. **Especificar** — deltas en `openspec/changes/{change}/specs/` (`sdd-spec`).
4. **Diseñar** — `design.md` si hay decisiones técnicas (`sdd-design`).
5. **Tareas** — `tasks.md` (`sdd-tasks`).
6. **Implementar** — código según tasks (`sdd-apply`).
7. **Verificar** — `verify-report.md` (`sdd-verify`).
8. **Archivar** — mover a `changes/archive/` y fusionar deltas en `specs/` (`sdd-archive`).

## Convenciones de este repo

- **Positivo / rojo**: resultado de sorteo que exige control (pantalla roja + registro). No equivale a “verde / buena jornada”.
- **Config de sorteo**: `backend/config.yaml` (embebido en imagen Docker backend).
- **Secrets**: solo en `.env` / `.env.prod` / GitHub Secrets; nunca en specs ni commits.
- **Frontend build-time**: `VITE_*` se inyecta en build (GitHub Actions o Docker build args).

## Documentación operativa existente

- [README.md](../README.md) — setup local y endpoints
- [docs/deploy-hostinger-ghcr.md](../docs/deploy-hostinger-ghcr.md) — deploy VPS + GHCR
- [AGENTS.md](../../AGENTS.md) — acuerdos de colaboración con IA (stack, seguridad)

## Estado inicial

- Specs baseline generadas el 2026-05-22 a partir del código en `main`.
- No hay cambios activos en `openspec/changes/` (listo para el primer change formal).
