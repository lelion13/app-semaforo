# Registro de control positivo

Dominio: persistencia de casos rojo completados (`POST /api/registro`).

## Requirements

### Requirement: Registro idempotente por sorteo

El sistema MUST tratar cada `sorteo_id` como único en `registros_rojos`.

#### Scenario: Primer registro de un sorteo

- GIVEN un `sorteo_id` válido que no existe en DB
- WHEN se envía `POST /api/registro` con legajo, nombre, apellido y `foto_base64` JPEG
- THEN MUST decodificar y guardar la foto en `{fotos.directorio}/{sorteo_id}.jpg`
- AND MUST insertar fila en `registros_rojos` con `email_enviado=false` inicialmente
- AND MUST responder `{ "ok": true }` si la persistencia en DB fue exitosa

#### Scenario: Reintento con mismo sorteo_id

- GIVEN ya existe un registro con el mismo `sorteo_id`
- WHEN se repite `POST /api/registro`
- THEN MUST responder `{ "ok": true }` sin duplicar fila

### Requirement: Validación de payload

El backend MUST validar el body con Pydantic.

| Campo | Regla |
|-------|-------|
| `legajo` | Numérico, requerido, max 50 chars |
| `nombre`, `apellido` | Requeridos, max 100 chars |
| `foto_base64` | MUST comenzar con `data:image/jpeg;base64,` |

#### Scenario: Foto inválida

- GIVEN `foto_base64` corrupto o formato incorrecto
- WHEN se invoca el endpoint
- THEN MUST responder HTTP 400 con detalle de foto inválida

### Requirement: Campos de seguimiento RRHH

Cada registro MUST incluir estado de control para dashboard.

| Campo | Default | Valores |
|-------|---------|---------|
| `estado_control` | `pendiente` | `pendiente`, `realizado`, `no_asistio` |
| `fecha_control` | null | Timestamp cuando pasa a `realizado` |
| `observacion_control` | null | Texto opcional |

### Requirement: Autenticación

`POST /api/registro` MUST exigir `X-API-Key` válido (middleware kiosk).

### Requirement: Email en el mismo request

Tras guardar en DB, el sistema MUST intentar envío de email inmediato.

#### Scenario: Email exitoso en primer intento

- GIVEN credenciales SMTP válidas
- WHEN el registro se persiste
- THEN MUST marcar `email_enviado=true` y limpiar `email_error`

#### Scenario: Email fallido en primer intento

- GIVEN fallo SMTP al enviar
- WHEN el registro se persiste correctamente
- THEN MUST responder `{ "ok": true }` igualmente
- AND MUST setear `email_enviado=false`, `email_intentos=1` y `email_error` con mensaje truncado

## Modelo de datos (resumen)

Tabla `registros_rojos`: `id`, `sorteo_id` (unique), `legajo`, `nombre`, `apellido`, `foto_path`, `fecha_hora`, `email_enviado`, `email_intentos`, `email_error`, `estado_control`, `fecha_control`, `observacion_control`.

Solo se persisten sorteos con resultado rojo completados. Los verdes no se registran.
