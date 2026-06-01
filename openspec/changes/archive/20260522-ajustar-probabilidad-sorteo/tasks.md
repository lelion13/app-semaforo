# Tasks: Ajustar probabilidad de sorteo

## 1. Configuración

- [x] 1.1 Cambiar `sorteo.probabilidad_rojo` de `30` a `10` en `backend/config.yaml`

## 2. CI/CD

- [x] 2.1 Push a `main` y verificar job `build-and-push-backend` en GitHub Actions

## 3. Deploy producción

- [x] 3.1 En VPS: `docker compose pull backend` + `up -d backend` (solo backend)

## 4. Verificación

- [x] 4.1 Confirmar en dashboard que registros positivos se persisten correctamente
- [x] 4.2 Operación kiosk funcional tras redeploy backend
