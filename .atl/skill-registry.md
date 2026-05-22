# Skill registry — app-semaforo

Generado para SDD. Relevamiento de skills y convenciones disponibles para agentes en este proyecto.

## Convenciones del proyecto

| Archivo | Propósito |
|---------|-----------|
| [AGENTS.md](../../../AGENTS.md) | Stack, seguridad, layout, acuerdos de colaboración |
| [README.md](../../../README.md) | Setup, endpoints, runbook |
| [docs/deploy-hostinger-ghcr.md](../../../docs/deploy-hostinger-ghcr.md) | Deploy GHCR + VPS |
| [openspec/README.md](../../../openspec/README.md) | Flujo SDD / OpenSpec |

## Skills SDD (orquestación de cambios)

| Skill | Uso |
|-------|-----|
| `sdd-init` | Inicializar contexto SDD (ya aplicado) |
| `sdd-explore` | Investigar ideas antes de un change |
| `sdd-propose` | Crear proposal.md |
| `sdd-spec` | Escribir delta specs |
| `sdd-design` | Documento de diseño técnico |
| `sdd-tasks` | Descomponer en tasks.md |
| `sdd-apply` | Implementar tasks |
| `sdd-verify` | Verificar contra specs |
| `sdd-archive` | Archivar change y fusionar specs |

## Skills Cursor (usuario)

| Skill | Trigger típico |
|-------|----------------|
| `api-design-principles` | Diseño/revisión de APIs REST |
| `create-rule` | Reglas persistentes `.cursor/rules` |
| `create-skill` | Authoring de skills |
| `canvas` | Artefactos analíticos interactivos |
| `split-to-prs` | Dividir trabajo en PRs pequeños |
| `babysit` | Mantener PR merge-ready (CI, comentarios) |
| `loop` | Tareas recurrentes en shell |
| `sdk` | Cursor TypeScript SDK |
| `microprompt` | Microapps Next.js / microprompt |

## Skills Claude (usuario)

| Skill | Trigger típico |
|-------|----------------|
| `go-testing` | Tests Go / Bubbletea |
| `skill-creator` | Crear skills Agent Skills spec |

## Reglas Cursor aplicables (workspace)

- Auth JWT + bcrypt en rutas protegidas
- Stack React/Tailwind + FastAPI/Pydantic
- No commitear secretos; validación Pydantic en API

## Comandos útiles (verify phase)

```bash
# Frontend typecheck + build
cd frontend && npm run build

# Backend syntax
python -m compileall backend

# Compose prod válido
docker compose -f docker-compose.prod.yml config
```

## Notas

- No hay `test_command` unificado configurado en `openspec/config.yaml` aún.
- Preferir cambios spec-first: proposal → delta spec → design → tasks → apply → verify → archive.
