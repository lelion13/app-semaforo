# Notificaciones por email

Dominio: envío SMTP al detectar un registro rojo y reintentos automáticos.

## Requirements

### Requirement: Envío inmediato al registrar

Tras `POST /api/registro` exitoso, el sistema MUST intentar enviar un email HTML con foto adjunta.

#### Scenario: Contenido del email

- GIVEN un registro rojo recién creado
- WHEN se envía el email
- THEN el asunto MUST incluir legajo y fecha/hora en `zona_horaria` (`Control requerido — Legajo {legajo} — dd/mm/yyyy HH:MM`)
- AND el cuerpo HTML MUST incluir nombre completo, legajo, fecha/hora local y texto de presentación al laboratorio
- AND MUST adjuntar `{sorteo_id}.jpg` desde `fotos.directorio`
- AND MUST enviar a todos los destinatarios en `email.destinatarios` de `config.yaml`

### Requirement: Configuración SMTP

| Fuente | Clave | Notas |
|--------|-------|-------|
| `config.yaml` | `email.smtp_host`, `smtp_port`, `smtp_user`, `remitente`, `destinatarios` | Host/puerto/usuario/destinos |
| Entorno | `EMAIL_PASSWORD` | Secret; MUST NOT commitearse |

El backend MUST fallar al arrancar si `EMAIL_PASSWORD` no está definido.

### Requirement: Reintentos programados

Un job APScheduler MUST ejecutarse cada `email_reintentos.intervalo_minutos` (default 5).

#### Scenario: Reintento tras fallo

- GIVEN registros con `email_enviado=false` y `email_error` no nulo
- WHEN corre el job
- THEN MUST reintentar envío
- AND MUST incrementar `email_intentos` en cada fallo
- AND MUST marcar `email_enviado=true` y limpiar `email_error` si el envío tiene éxito

#### Scenario: Máximo de intentos superado

- GIVEN `email_intentos >= email_reintentos.max_intentos` (default 5)
- WHEN corre el job
- THEN MUST setear `email_error` a `MAX_INTENTOS_SUPERADOS`
- AND MUST NOT seguir reintentando ese registro

### Requirement: Errores no expuestos en logs de consola

Los fallos SMTP MUST persistirse en `registros_rojos.email_error`. No es obligatorio loguearlos en stdout (verificación vía DB o dashboard).

#### Scenario: Diagnóstico de fallo SMTP

- GIVEN un registro con `email_enviado=false`
- WHEN RRHH o operaciones consultan la fila
- THEN `email_error` MUST contener el motivo (ej. `535 Authentication failed`)

## Operación

- Corregir `EMAIL_PASSWORD` en `.env.prod` requiere reinicio del contenedor backend.
- Tras corregir credenciales, MAY resetear manualmente `email_intentos` y `email_error` en DB para reencolar reintentos.
