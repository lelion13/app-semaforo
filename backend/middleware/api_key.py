from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import get_settings


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/health":
            return await call_next(request)

        if request.url.path.startswith("/api/"):
            settings = get_settings()
            provided_key = request.headers.get("X-API-Key", "")
            if provided_key != settings.api_key:
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        return await call_next(request)
