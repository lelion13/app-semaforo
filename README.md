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

- `openspec/`: especificaciones SDD (fuente de verdad) y carpeta de cambios futuros. Ver [openspec/README.md](openspec/README.md).

- `docs/`: runbooks de deploy y documentación operativa.

- `.atl/skill-registry.md`: registro de skills y convenciones para agentes.



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

## Metodo unico de deploy (GitHub -> Hostinger)

Fuente de verdad:

- Rama oficial de deploy: `main`.
- El proyecto en Hostinger debe desplegar siempre desde `main`.
- No usar ramas alternativas para produccion.

Regla operativa:

1. Antes de trabajar: `git pull --ff-only origin main`.
2. Hacer cambios, commit y push a `main`.
3. En Hostinger presionar `Desplegar`.
4. Validar logs y ejecutar migraciones.

## Runbook VPS Hostinger + Traefik

Prerequisitos:

1. Traefik levantado (como servicio independiente) con Docker provider y resolver `letsencrypt`.
2. DNS `A` record de `control.lionapp.cloud` apuntando al VPS.
3. Puertos 80 y 443 abiertos en firewall.

Variables obligatorias en Hostinger Project Environment:

```env
POSTGRES_DB=control_drogas
POSTGRES_USER=user
POSTGRES_PASSWORD=definir-password-fuerte
DATABASE_URL=postgresql+asyncpg://user:definir-password-fuerte@db:5432/control_drogas
API_KEY=clave-secreta-minimo-32-caracteres
EMAIL_PASSWORD=password-smtp
FRONTEND_URLS=https://control.lionapp.cloud
VITE_API_URL=https://control.lionapp.cloud
VITE_API_KEY=clave-secreta-minimo-32-caracteres
VITE_EMPRESA_NOMBRE=Clinica Monte Grande
VITE_EMPRESA_LOGO_URL=https://clinicamg.com.ar/wp-content/uploads/2025/08/logos-azul.png
```

Nota: en este compose, `backend` y `frontend` toman variables desde el entorno del proyecto (no depende de `backend/.env` ni `frontend/.env` dentro del VPS al desplegar por Hostinger).

Checklist rapido anti-falla de `VITE_API_URL` (antes de Deploy):

1. Verificar que exista `VITE_API_URL` en Project Environment.
2. Valor esperado en produccion: `https://control.lionapp.cloud` (sin barra final).
3. Rebuild completo del frontend al cambiar variables (`Deploy` con build, no solo restart).
4. Si hay pantalla en blanco, revisar logs de build del frontend y confirmar que no aparezca `Falta VITE_API_URL`.

Pasos de despliegue:

1. Confirmar que el repo en Hostinger apunta a `main`.
2. Confirmar variables del proyecto (lista obligatoria de arriba).
3. Verificar labels Traefik de `docker-compose.yml` para `control.lionapp.cloud`.
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
- [ ] frontend sin error de consola `Falta VITE_API_URL`.
- [ ] emails salen con credenciales SMTP reales.
- [ ] volumen de `db_data` y carpeta `backend/fotos` incluidos en backup.

## Rollback y troubleshooting rapido

Si falla deploy:

1. Revisar logs de `backend` y `frontend`.
2. Confirmar variables de entorno en Hostinger Project.
3. Re-ejecutar migraciones: `docker compose exec backend alembic upgrade head`.

Si frontend queda en blanco:

1. Verificar que `frontend/Dockerfile` tenga `ARG` + `ENV` de `VITE_*` antes de `npm run build`.
2. Verificar en compose `frontend.build.args` con `VITE_*`.
3. Rebuild frontend y hard refresh/incognito.

Si se hizo hotfix por SSH:

1. Replicar el cambio en repo local.
2. Push a `main`.
3. Volver a desplegar desde Hostinger para re-alinear servidor con GitHub.

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


