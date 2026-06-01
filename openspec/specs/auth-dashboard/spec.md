# Auth y dashboard RRHH

Dominio: acceso protegido a `/dashboard` y APIs bajo `/api/auth/*` y `/api/dashboard/*`.

## Requirements

### Requirement: Autenticación JWT para dashboard

Los endpoints de dashboard MUST exigir `Authorization: Bearer <access_token>` válido.

#### Scenario: Login exitoso

- GIVEN un usuario activo en `usuarios_dashboard` con contraseña bcrypt válida
- WHEN invoca `POST /api/auth/login` con email y password
- THEN MUST responder access token JWT y datos básicos del usuario (`admin` o `rrhh`)

#### Scenario: Token inválido o expirado

- GIVEN request sin Bearer o con JWT inválido
- WHEN accede a `GET /api/dashboard/registros`
- THEN MUST responder HTTP 401 con mensaje genérico

### Requirement: Hash de contraseñas

Las contraseñas MUST almacenarse únicamente con bcrypt (salt por hash). MUST NOT persistirse ni loguearse texto plano.

#### Scenario: Definir contraseña por enlace

- GIVEN token de tipo `set_password` o `reset_password` válido y no usado
- WHEN el usuario envía nueva clave (mín. 10 caracteres) a `POST /api/auth/confirm-password`
- THEN MUST actualizar `password_hash` y marcar token como usado

### Requirement: Bootstrap del primer admin

#### Scenario: Sin admins en sistema

- GIVEN no existe ningún usuario con rol `admin`
- WHEN se consulta `GET /api/auth/bootstrap-status`
- THEN MUST indicar `needs_bootstrap: true`
- AND `POST /api/auth/bootstrap-admin` MUST permitir crear el primer admin (rate limited)

#### Scenario: Bootstrap ya realizado

- GIVEN ya existe al menos un admin
- WHEN se intenta bootstrap de nuevo
- THEN MUST responder HTTP 403

### Requirement: Roles y autorización

| Rol | Permisos |
|-----|----------|
| `admin` | Dashboard + crear usuarios (`POST /api/auth/users`) |
| `rrhh` | Dashboard (listar, actualizar estado, ver foto) |

#### Scenario: RRHH actualiza seguimiento

- GIVEN usuario autenticado con rol `admin` o `rrhh`
- WHEN invoca `PATCH /api/dashboard/registros/{id}` con `estado_control`
- THEN MUST persistir estado y observación
- AND MUST setear `fecha_control` si el estado es `realizado`

### Requirement: API pública kiosk vs dashboard

| Ruta | Auth |
|------|------|
| `/api/sorteo`, `/api/registro` | `X-API-Key` |
| `/api/dashboard/*` | JWT (middleware delega; validación en dependencias) |
| `/api/auth/login`, bootstrap, reset | Público con rate limit donde aplique |
| `/api/health` | Público |

El middleware MUST NOT exigir API key en rutas de auth/dashboard protegidas por JWT.

### Requirement: Resumen dashboard

`GET /api/dashboard/resumen` MUST devolver conteos de `positivos_hoy` (registros del día UTC) y `pendientes` (`estado_control=pendiente`).

### Requirement: Seguridad de tokens y secretos

- `JWT_SECRET` MUST tener al menos 32 caracteres (env).
- MUST NOT loguearse JWTs, hashes de password ni tokens de reset en respuestas o logs.

## Frontend dashboard

- Ruta `/dashboard`: login si no hay token en almacenamiento local del cliente.
- Token JWT guardado en cliente para llamadas API autenticadas.
- UI: tabla de registros, filtros de estado, modal de foto, creación de usuarios (admin).
- Componentes UI en `frontend/src/components/ui/*` (patrón shadcn + Tailwind).

### Requirement: Acceso inicial y recuperación de contraseña

El sistema MUST NOT proveer credenciales por defecto en `.env` ni en el repositorio.

#### Scenario: Primer admin (bootstrap)

- GIVEN `GET /api/auth/bootstrap-status` responde `needs_bootstrap: true`
- WHEN el operador abre `https://control.lionapp.cloud/user`
- THEN MUST poder crear el primer admin (email + contraseña bcrypt)
- AND tras bootstrap, `needs_bootstrap` MUST ser `false`

#### Scenario: Bootstrap ya realizado

- GIVEN `needs_bootstrap: false`
- WHEN se abre `/user`
- THEN MUST mostrarse flujo de recuperación de contraseña por email (enlace de uso único, ~60 min)
- AND el login operativo MUST ser en `/dashboard` con el email registrado en `usuarios_dashboard`

#### Scenario: Consulta de usuarios en VPS

- GIVEN olvido del email de admin
- WHEN el operador ejecuta SQL en `usuarios_dashboard` (solo lectura de email/rol)
- THEN MUST identificar el email de login sin exponer `password_hash`

Documentación operativa: [docs/deploy-hostinger-ghcr.md](../../docs/deploy-hostinger-ghcr.md) sección 8.
