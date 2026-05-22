# Kiosk UI (tablet)

Dominio: experiencia del empleado en la ruta raíz `/` (componente `KioskApp`).

## Requirements

### Requirement: Inicialización de cámara obligatoria

La aplicación MUST solicitar permiso de cámara frontal al cargar (`getUserMedia`, `facingMode: 'user'`).

#### Scenario: Permiso concedido

- GIVEN el navegador concede acceso a la cámara
- WHEN la app termina de inicializar
- THEN MUST mantener el stream activo en segundo plano sin mostrar preview al empleado
- AND MUST mostrar el estado IDLE con botón "Iniciar control"

#### Scenario: Permiso denegado

- GIVEN el permiso de cámara es denegado o la cámara no está disponible
- WHEN la app carga
- THEN MUST mostrar pantalla bloqueante de error de cámara
- AND MUST NOT mostrar el botón "Iniciar control"
- AND MUST NOT ofrecer flujo alternativo sin foto

### Requirement: Máquina de estados del flujo kiosk

El frontend MUST implementar los estados: `ERROR_CAMARA`, `IDLE`, `LOADING`, `VERDE`, `ROJO`, `ENVIANDO`, `CONFIRMADO`.

#### Scenario: Flujo verde

- GIVEN estado IDLE y cámara lista
- WHEN el empleado pulsa "Iniciar control" y el sorteo devuelve `verde`
- THEN MUST mostrar pantalla verde con mensaje de buena jornada
- AND MUST volver automáticamente a IDLE tras 5 segundos

#### Scenario: Flujo rojo

- GIVEN el sorteo devuelve `rojo`
- WHEN entra al estado ROJO
- THEN MUST capturar un frame JPEG en base64 automáticamente (sin mostrar foto al empleado)
- AND MUST mostrar formulario bloqueante (legajo numérico, nombre, apellido)
- AND MUST NOT permitir volver a IDLE sin completar el registro exitosamente

#### Scenario: Envío de registro

- GIVEN formulario válido y foto capturada
- WHEN el empleado confirma
- THEN MUST pasar a ENVIANDO
- AND MUST invocar `POST /api/registro`
- AND tras éxito MUST mostrar CONFIRMADO y permitir "Finalizar" → IDLE

### Requirement: Persistencia de rojo pendiente

El frontend MUST usar `sessionStorage` para recuperar sorteos rojos no completados.

#### Scenario: Recarga con rojo pendiente

- GIVEN un sorteo devolvió `rojo` y se guardó `{ sorteoId, estado: "rojo_pendiente" }` en sessionStorage
- WHEN el empleado recarga la página antes de completar el formulario
- THEN MUST restaurar estado ROJO con el mismo `sorteo_id`
- AND MUST NOT ejecutar un nuevo sorteo automáticamente

#### Scenario: Registro completado

- GIVEN un registro rojo se envió correctamente
- WHEN el flujo llega a CONFIRMADO y el usuario finaliza
- THEN MUST limpiar sessionStorage del rojo pendiente

### Requirement: Cliente API kiosk

Las llamadas a `/api/sorteo` y `/api/registro` MUST incluir `X-API-Key` desde `VITE_API_KEY` y usar `VITE_API_URL` como base.

#### Scenario: URL de API en producción

- GIVEN despliegue en `https://control.lionapp.cloud`
- WHEN el frontend compilado invoca la API
- THEN MUST usar rutas `/api/...` sobre el mismo origen (proxy Nginx → backend)
- AND `VITE_API_URL` MUST estar definida en build-time (GitHub Secrets / Docker build args)

## Rutas SPA

| Ruta | Componente | Uso |
|------|------------|-----|
| `/` | `KioskApp` | Tablet de control |
| `/dashboard` | `DashboardPage` | RRHH (spec auth-dashboard) |
| `/user` | `SetupPage` | Bootstrap admin / reset password |
