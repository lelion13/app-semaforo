from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import get_settings


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/api/health", "/api/auth/bootstrap-status", "/api/auth/bootstrap-admin", "/api/auth/login", "/api/auth/request-password-reset", "/api/auth/confirm-password"}:
            return await call_next(request)
        if request.url.path.startswith("/api/dashboard/") or request.url.path == "/api/auth/users":
            return await call_next(request)

        if request.url.path.startswith("/api/"):
            settings = get_settings()
            provided_key = request.headers.get("X-API-Key", "")
            if provided_key != settings.api_key:
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        return await call_next(request)
