# Sistema de control antidrogas



Aplicacion full-stack para sorteo de control antidrogas en tablet fija, con captura automatica de foto en caso rojo, registro en PostgreSQL y notificacion por email con reintentos.



## Stack



- Frontend: React + Vite + TypeScript + Tailwind CSS.

- Backend: FastAPI + SQLAlchemy async + Alembic.

- Base de datos: PostgreSQL 16.

- Email: fastapi-mail.

- Scheduler: APScheduler.



## Estructura



- `backend/`: API, modelos, migraciones y servicios.

- `frontend/`: UI, hooks, cliente API y build Nginx.

- `docker-compose.yml`: db + backend + frontend.



## Configuracion backend



1. Copiar `backend/.env.example` a `backend/.env`.

2. Completar `DATABASE_URL`, `API_KEY`, `EMAIL_PASSWORD`, y orígenes CORS (`FRONTEND_URLS` o `FRONTEND_URL`).

3. Ajustar `backend/config.yaml` (probabilidad, SMTP, empresa, destinos, fotos, reintentos).



Variables esperadas:



```env

DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/control_drogas

API_KEY=clave-secreta-minimo-32-caracteres

EMAIL_PASSWORD=password-smtp

# Lista separada por comas. En produccion usar dominio publico real.
FRONTEND_URLS=https://control.lionapp.cloud

```



Compatibilidad: si solo definis `FRONTEND_URL=https://control.lionapp.cloud`, CORS usa un único origen (comportamiento anterior).



## Configuracion frontend



1. Copiar `frontend/.env.example` a `frontend/.env`.

2. Completar (la URL base debe coincidir con el host HTTPS que usan los clientes; se inyecta en el build):



```env

VITE_API_URL=https://control.lionapp.cloud

VITE_API_KEY=clave-secreta-minimo-32-caracteres

```



## Ejecucion local



### Backend



```bash

cd backend

pip install -r requirements.txt

alembic upgrade head

uvicorn main:app --reload

```



### Frontend



```bash

cd frontend

npm install

npm run dev

```



## Docker Compose (produccion con Traefik en Hostinger)



```bash
docker compose up -d --build
```



Servicios:

- Frontend: interno en Docker, publicado por Traefik via `Host(control.lionapp.cloud)`.
- Backend: interno en Docker (`backend:8000`), accesible por `/api` desde frontend.
- DB: interna en Docker (`db:5432`), sin exposicion publica.

## Runbook VPS Hostinger + Traefik

Prerequisitos:

1. Traefik levantado (como servicio independiente) con Docker provider y resolver `letsencrypt`.
2. DNS `A` record de `control.lionapp.cloud` apuntando al VPS.
3. Puertos 80 y 443 abiertos en firewall.

Pasos de despliegue:

1. Clonar proyecto en VPS y crear `backend/.env` y `frontend/.env` desde los `.env.example`.
2. Verificar que `control.lionapp.cloud` este configurado en:
   - `frontend/.env`
   - `backend/.env`
   - labels Traefik de `docker-compose.yml`
3. Construir y subir servicios:
   - `docker compose up -d --build`
4. Ejecutar migraciones:
   - `docker compose exec backend alembic upgrade head`
5. Verificar salud:
   - `https://control.lionapp.cloud/api/health` debe responder `{"status":"ok"}`.
6. Verificar certificado:
   - abrir `https://control.lionapp.cloud` y confirmar TLS valido emitido por Let's Encrypt.

Checklist post-deploy:

- [ ] `docker compose ps` sin servicios en estado restarting/unhealthy.
- [ ] `frontend` responde por HTTPS.
- [ ] llamadas a `/api` funcionan desde el navegador sin error CORS.
- [ ] emails salen con credenciales SMTP reales.
- [ ] volumen de `db_data` y carpeta `backend/fotos` incluidos en backup.

## HTTPS local para tablet (mkcert, solo entornos locales/LAN)



1. Instalar `mkcert` en la PC anfitriona.

2. Ejecutar:

   - `mkcert -install`

   - `mkcert -cert-file frontend/certs/control.local.pem -key-file frontend/certs/control.local-key.pem control.lionapp.cloud control.clno0026 control.local localhost 127.0.0.1`

3. En cada cliente (PC, tablet), resolver `control.lionapp.cloud` hacia la IP del servidor (archivo hosts, DNS interno o router). Opcional: mismo criterio para `control.clno0026` y `control.local` si los usás en paralelo.

4. Instalar y confiar la CA raiz de `mkcert` en la tablet.

5. Reconstruir el frontend tras cambiar `frontend/.env` (Vite embebe `VITE_API_URL`):

   - `docker compose up -d --build frontend backend`



### Compatibilidad de nombres



- **Canónico**: `https://control.lionapp.cloud` (coincide con `VITE_API_URL` y certificado SAN).

- **Transición**: `https://control.local` sigue sirviendo el mismo Nginx si el nombre está en `server_name` y en el certificado.

- **Pruebas en la misma máquina**: `https://localhost` (requiere estar en SAN y `FRONTEND_URLS` debe incluir `https://localhost` para CORS).



## Endpoints



- `GET /api/health` (publico): `{ "status": "ok" }`

- `POST /api/sorteo` (requiere `X-API-Key`)

- `POST /api/registro` (requiere `X-API-Key`)

## Migracion recomendada a JWT (fase siguiente)

La API key actual se inyecta en frontend (`VITE_API_KEY`) y queda visible para cualquier usuario con acceso al navegador.

Para produccion segura:

1. Implementar login y emision de JWT en backend.
2. Proteger rutas de negocio con validacion JWT.
3. Actualizar frontend para enviar `Authorization: Bearer <token>`.
4. Retirar gradualmente `X-API-Key` y `VITE_API_KEY`.



## Flujo de UI



- `ERROR_CAMARA`: bloqueante sin boton.

- `IDLE`: boton `Iniciar control`.

- `LOADING`: spinner.

- `VERDE`: mensaje y retorno a `IDLE` en 5 segundos.

- `ROJO`: captura automatica + formulario bloqueante.

- `ENVIANDO`: spinner bloqueante.

- `CONFIRMADO`: mensaje final + `Finalizar`.



## Reintentos de email



- Job periodico cada `email_reintentos.intervalo_minutos`.

- Reintenta registros con `email_enviado=false` y `email_error` no nulo.

- Maximo `email_reintentos.max_intentos`.

- Si supera maximo: `email_error=MAX_INTENTOS_SUPERADOS`.



## Troubleshooting



- Permiso camara denegado: habilitar acceso en navegador y recargar pagina.

- Error SMTP: verificar `EMAIL_PASSWORD`, host/puerto y remitente.

- CORS: el origen del navegador (URL en la barra) debe estar en `FRONTEND_URLS` o coincidir con `FRONTEND_URL`.

- Migraciones: ejecutar `alembic upgrade head` antes de iniciar API.

- Nombre no resuelve: registrar `control.lionapp.cloud` (y aliases opcionales) en DNS o `hosts` antes de probar.


