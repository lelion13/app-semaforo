from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from models import UsuarioDashboard
from services.auth_service import decode_access_token


@dataclass(frozen=True)
class AuthContext:
    user: UsuarioDashboard


_rate_limit_store: dict[str, list[datetime]] = {}


def enforce_rate_limit(request: Request, *, key: str, max_attempts: int = 5, window_seconds: int = 60) -> None:
    ip = request.client.host if request.client else "unknown"
    bucket_key = f"{key}:{ip}"
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)
    attempts = [at for at in _rate_limit_store.get(bucket_key, []) if at > cutoff]
    if len(attempts) >= max_attempts:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many attempts")
    attempts.append(now)
    _rate_limit_store[bucket_key] = attempts


async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> AuthContext:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = await session.scalar(select(UsuarioDashboard).where(UsuarioDashboard.id == user_id))
    if user is None or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return AuthContext(user=user)


def require_roles(*roles: str):
    async def _require(ctx: AuthContext = Depends(get_current_user)) -> AuthContext:
        if ctx.user.rol.value not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return ctx

    return _require
