# Sorteo antidrogas

Dominio: lógica aleatoria de selección para control en kiosk (`POST /api/sorteo`).

## Requirements

### Requirement: Sorteo criptográficamente aleatorio

El sistema MUST generar un entero uniforme en `[0, 99]` usando `secrets.randbelow(100)` por cada invocación de sorteo.

#### Scenario: Sorteo dentro del cupo diario

- GIVEN el conteo de registros rojos del día calendario UTC es menor que `sorteo.max_rojos_dia`
- WHEN un cliente autenticado con `X-API-Key` invoca `POST /api/sorteo`
- THEN el backend MUST evaluar `numero < sorteo.probabilidad_rojo`
- AND MUST responder `{ "resultado": "rojo" | "verde", "sorteo_id": "<uuid-v4>" }`
- AND MUST NOT persistir el resultado en base de datos en este paso

#### Scenario: Probabilidad configurada al 30%

- GIVEN `sorteo.probabilidad_rojo` es `30` en `backend/config.yaml`
- WHEN se ejecutan sorteos independientes bajo el cupo diario
- THEN cada sorteo MUST tener probabilidad aproximada del 30% de resultado `rojo` y 70% de `verde`
- AND los sorteos MUST ser estadísticamente independientes entre sí (sin memoria de resultados anteriores)

### Requirement: Tope diario de casos positivos registrados

El sistema MUST forzar resultado `verde` cuando ya se alcanzó el cupo diario de registros completados.

#### Scenario: Cupo diario alcanzado

- GIVEN existen `N` filas en `registros_rojos` con `fecha_hora` dentro del día calendario UTC actual
- AND `N >= sorteo.max_rojos_dia` (default `5`)
- WHEN se invoca `POST /api/sorteo`
- THEN el backend MUST responder `resultado: "verde"` sin aplicar aleatoriedad
- AND MUST generar un nuevo `sorteo_id`

#### Scenario: Cupo diario no alcanzado

- GIVEN existen menos de `max_rojos_dia` registros rojos completados hoy (UTC)
- WHEN se invoca `POST /api/sorteo`
- THEN el sistema MUST aplicar la probabilidad configurada normalmente

### Requirement: Conteo diario basado en registros completados

El cupo diario MUST contar únicamente registros persistidos en `registros_rojos`, no sorteos rojos abandonados.

#### Scenario: Sorteo rojo sin formulario enviado

- GIVEN un sorteo devolvió `rojo` pero el empleado no completó `POST /api/registro`
- WHEN se consulta el cupo para el sorteo siguiente
- THEN ese sorteo MUST NOT incrementar el contador diario
- AND el siguiente sorteo MUST seguir sujeto a probabilidad completa (si no se alcanzó el cupo)

### Requirement: Configuración de sorteo

Los parámetros de sorteo MUST leerse de `backend/config.yaml` al arrancar el backend.

| Clave | Default | Descripción |
|-------|---------|-------------|
| `sorteo.probabilidad_rojo` | — | Entero 0–100; umbral exclusivo superior para rojo |
| `sorteo.max_rojos_dia` | `5` | Máximo de registros rojos por día UTC antes de forzar verde |

#### Scenario: Cambio de configuración

- GIVEN se modifica `backend/config.yaml` en el repositorio
- WHEN se despliega producción
- THEN MUST reconstruirse y redesplegarse la imagen backend para que el cambio surta efecto

### Requirement: Autenticación del endpoint

`POST /api/sorteo` MUST exigir header `X-API-Key` válido. `GET /api/health` MUST permanecer público.

## Notas operativas

- Dos resultados `rojo` consecutivos con probabilidad 30% es esperable (~9% de ocurrencia en pares independientes).
- El tope diario usa timezone UTC; en Argentina (UTC-3) el “día” del cupo puede no coincidir con el día local de operación.
- Concurrencia extrema MAY permitir superar el cupo en una ventana muy corta (sin lock transaccional en sorteo).
