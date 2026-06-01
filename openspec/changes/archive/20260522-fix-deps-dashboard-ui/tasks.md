# Tasks: Fix deps dashboard UI

## 1. Dependencias

- [x] 1.1 Instalar deps runtime en `frontend/package.json`
- [x] 1.2 Actualizar `frontend/package-lock.json`

## 2. Verificación local

- [x] 2.1 `cd frontend && npm run build` exitoso

## 3. CI/CD

- [x] 3.1 Push a `main` y verificar job `build-and-push-frontend` en verde

## 4. Deploy producción

- [x] 4.1 En VPS: `docker compose pull frontend` + `up -d frontend`
