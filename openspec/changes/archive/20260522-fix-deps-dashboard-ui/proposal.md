# Proposal: Corregir dependencias frontend del dashboard UI

## Intent

Restaurar el build de producción del frontend en GitHub Actions (GHCR) tras el refactor UI del dashboard.

## Problema

El commit de refactor dashboard (`App.tsx` + componentes `components/ui/*`) importaba librerías no declaradas en `package.json`. El CI ejecuta `npm run build` (`tsc -b && vite build`) y fallaba con errores TS2307:

- `lucide-react`
- `class-variance-authority`
- `clsx`, `tailwind-merge`
- `@radix-ui/react-slot`, `@radix-ui/react-dialog`, `@radix-ui/react-select`

## Cambio

Agregar las dependencias anteriores a `frontend/package.json` y actualizar `package-lock.json`.

## Alcance

- Incluye: deps npm, verificación local `npm run build`, push y publicación `app-semaforo-frontend:latest`.
- Excluye: cambios de UI, cambios de backend, nuevas features.

## Rollback

Revertir commit de deps; el frontend en GHCR volvería a la imagen anterior (`sha-*` pin en `.env.prod`).
