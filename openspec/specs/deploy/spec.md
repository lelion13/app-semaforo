# Deploy e infraestructura

Dominio: empaquetado, CI/CD y producción en Hostinger VPS con Traefik.

## Requirements

### Requirement: Servicios Docker en producción

Producción MUST usar `docker-compose.prod.yml` con imágenes GHCR (no build en VPS salvo emergencia).

| Servicio | Imagen | Exposición |
|----------|--------|------------|
| `db` | postgres:16 | Solo red interna |
| `backend` | ghcr.io/lelion13/app-semaforo-backend | `expose: 8000` |
| `frontend` | ghcr.io/lelion13/app-semaforo-frontend | `expose: 80` + labels Traefik |

#### Scenario: Routing Traefik

- GIVEN Traefik externo con resolver `letsencrypt`
- WHEN llega tráfico HTTPS a `Host(`control.lionapp.cloud`)`
- THEN MUST enrutar al contenedor frontend puerto 80
- AND Nginx del frontend MUST proxy `/api/` → `backend:8000/api/`
- AND MUST NOT exponer públicamente puertos de Postgres ni backend

### Requirement: CI/CD GitHub Actions

Push a `main` MUST disparar workflow `Docker Publish GHCR` que construye y publica:

- `ghcr.io/lelion13/app-semaforo-backend:latest` y tag `sha-{short}`
- `ghcr.io/lelion13/app-semaforo-frontend:latest` y tag `sha-{short}`

#### Scenario: Build frontend con variables Vite

- GIVEN secrets de repo `VITE_API_URL`, `VITE_API_KEY`, `VITE_EMPRESA_NOMBRE`, `VITE_EMPRESA_LOGO_URL`
- WHEN corre el job de frontend
- THEN MUST pasarlas como build-args al Dockerfile
- AND el bundle MUST NOT lanzar error `Falta VITE_API_URL` en runtime

### Requirement: Variables de entorno producción

Archivo `.env.prod` en VPS (no commitear). Mínimo:

| Variable | Servicio | Build/Runtime |
|----------|----------|---------------|
| `POSTGRES_*`, `DATABASE_URL` | db, backend | Runtime |
| `API_KEY` | backend | Runtime |
| `EMAIL_PASSWORD` | backend | Runtime |
| `FRONTEND_URLS`, `APP_BASE_URL` | backend | Runtime |
| `JWT_SECRET`, `JWT_*` | backend | Runtime |
| `VITE_*` | frontend (GHCR build) | Build-time en CI |
| `IMAGE_TAG` | compose | Runtime (opcional pin SHA) |

`DATABASE_URL` en Docker MUST usar host `db:5432`, no `localhost`.

### Requirement: Migraciones Alembic

Después de deploy que incluya cambios de schema, operaciones MUST ejecutar:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend alembic upgrade head
```

Alembic MUST usar driver sync (`psycopg2`) derivado de `DATABASE_URL` async.

### Requirement: Persistencia

- Volumen `db_data` para PostgreSQL.
- Bind mount `./backend/fotos:/app/fotos` para imágenes de registros.

### Requirement: Healthchecks

- Backend: `GET /api/health` → `{ "status": "ok" }`
- Frontend: HTTP 200 en `/`

## Entornos

| Entorno | Compose | TLS |
|---------|---------|-----|
| Local dev | `docker-compose.yml` | Opcional / mkcert |
| Producción VPS | `docker-compose.prod.yml` | Traefik + Let's Encrypt |

## Documentación relacionada

- [docs/deploy-hostinger-ghcr.md](../../docs/deploy-hostinger-ghcr.md)
- [README.md](../../README.md)
