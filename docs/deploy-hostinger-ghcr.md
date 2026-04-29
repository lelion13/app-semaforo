# Deploy en Hostinger VPS con imágenes GHCR

Este flujo evita compilar en la VPS. GitHub compila y publica imágenes en GHCR; la VPS solo hace `pull` y `up -d`.

## 1) Preparar variables en GitHub (una sola vez)

En `lelion13/app-semaforo` crear estos **Repository Secrets**:

- `VITE_API_URL`
- `VITE_API_KEY`
- `VITE_EMPRESA_NOMBRE`
- `VITE_EMPRESA_LOGO_URL`

El workflow `.github/workflows/docker-publish.yml` publicará:

- `ghcr.io/lelion13/app-semaforo-backend:latest`
- `ghcr.io/lelion13/app-semaforo-frontend:latest`
- `ghcr.io/lelion13/app-semaforo-backend:sha-<shortsha>`
- `ghcr.io/lelion13/app-semaforo-frontend:sha-<shortsha>`

## 2) Publicar imágenes desde GitHub

1. Hacer push a `main` (o ejecutar manualmente `workflow_dispatch`).
2. Verificar en GitHub Actions que el job finalizó en verde.
3. Verificar en GHCR que existan tags nuevos.

## 3) Preparar VPS (primera vez)

En la VPS (Ubuntu), dentro del proyecto `/docker/app-semaforo`:

1. Copiar `docker-compose.prod.yml` del repo.
2. Crear `.env.prod` desde `.env.prod.example`.
3. Completar secretos reales:
   - `POSTGRES_PASSWORD`
   - `API_KEY` (32+ caracteres)
   - `JWT_SECRET` (32+ caracteres)
   - `EMAIL_PASSWORD`
4. Configurar auth:
   - `APP_BASE_URL=https://control.lionapp.cloud`
   - `JWT_ALGORITHM=HS256`
   - `JWT_EXPIRES_MINUTES=480`
5. Revisar `DATABASE_URL` para que use host `db` (`...@db:5432/...`).

Comandos:

```bash
cd /docker/app-semaforo
cp .env.prod.example .env.prod
```

## 4) Desplegar o actualizar en VPS

```bash
cd /docker/app-semaforo
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

Nota: el fix de Alembic convierte `postgresql+asyncpg://...` a URL sync solo para migraciones, por lo que `alembic upgrade head` ya funciona en producción.

## 5) Rollback rápido por tag

1. Cambiar `IMAGE_TAG` en `.env.prod` a un tag estable, por ejemplo `sha-abc1234`.
2. Ejecutar:

```bash
cd /docker/app-semaforo
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

## 6) Checklist post-deploy (health, dominio, TLS)

1. `docker compose ... ps` muestra `db`, `backend`, `frontend` en `running` y con `healthy` cuando aplique.
2. `https://control.lionapp.cloud` responde 200/304 y carga frontend.
3. Certificado TLS válido emitido por Traefik (Let’s Encrypt).
4. Backend responde healthcheck interno (`/api/health`) sin reinicios constantes.
5. Flujo de app básico operativo (login/consulta principal).
6. La migración está aplicada: `docker compose ... exec backend alembic current`.

## 7) PWA instalable (modo app)

La app ya está configurada como PWA instalable (`display: standalone`).

- En Chrome/Edge Desktop: abrir `https://control.lionapp.cloud` y usar `Instalar app`.
- En Android (Chrome): menú del navegador -> `Instalar app` o `Agregar a pantalla principal`.
- En iOS (Safari): `Compartir` -> `Añadir a pantalla de inicio`.

Esto no habilita modo offline completo; la instalación es para experiencia tipo app y acceso directo.

## 8) Dashboard RRHH y usuarios

- Setup inicial del primer admin: `https://control.lionapp.cloud/user`
  - Solo funciona si no existe ningún usuario `admin`.
- Login de gestión: `https://control.lionapp.cloud/dashboard`
- Flujo de usuarios:
  - Admin crea usuario (`admin` o `rrhh`) desde dashboard.
  - El usuario recibe link de uso único por email para definir clave (vence en 60 min).
  - Recuperación de clave también usa link de uso único.

## 9) Notas de compatibilidad con Traefik

- No se modifica el proyecto `traefik-wpez`.
- Se mantienen labels actuales en `frontend`:
  - `traefik.http.routers.app-semaforo.rule=Host(\`control.lionapp.cloud\`)`
  - `traefik.http.routers.app-semaforo.entrypoints=websecure`
  - `traefik.http.routers.app-semaforo.tls.certresolver=letsencrypt`
- No se agregan redes Traefik nuevas.
