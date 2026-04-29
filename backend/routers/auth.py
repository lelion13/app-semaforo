from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db_session
from models import AuthToken, RolUsuario, TipoAuthToken, UsuarioDashboard
from schemas import (
    AuthUser,
    BootstrapAdminRequest,
    BootstrapStatusResponse,
    ConfirmPasswordRequest,
    CreateUserRequest,
    GenericMessageResponse,
    LoginRequest,
    LoginResponse,
    PasswordTokenRequest,
)
from security import enforce_rate_limit, require_roles
from services.auth_service import (
    create_access_token,
    generate_raw_token,
    hash_password,
    hash_raw_token,
    verify_password,
)
from services.email_service import send_password_link_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/bootstrap-status", response_model=BootstrapStatusResponse)
async def bootstrap_status(session: AsyncSession = Depends(get_db_session)) -> BootstrapStatusResponse:
    admin_count = await session.scalar(
        select(func.count()).select_from(UsuarioDashboard).where(UsuarioDashboard.rol == RolUsuario.admin)
    )
    return BootstrapStatusResponse(needs_bootstrap=int(admin_count or 0) == 0)


@router.post("/bootstrap-admin", response_model=GenericMessageResponse)
async def bootstrap_admin(
    payload: BootstrapAdminRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> GenericMessageResponse:
    enforce_rate_limit(request, key="bootstrap")
    admin_count = await session.scalar(
        select(func.count()).select_from(UsuarioDashboard).where(UsuarioDashboard.rol == RolUsuario.admin)
    )
    if int(admin_count or 0) > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bootstrap disabled")

    email = payload.email.lower().strip()
    exists = await session.scalar(select(UsuarioDashboard).where(UsuarioDashboard.email == email))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    user = UsuarioDashboard(
        nombre=payload.nombre.strip(),
        apellido=payload.apellido.strip(),
        email=email,
        rol=RolUsuario.admin,
        password_hash=hash_password(payload.password),
        activo=True,
    )
    session.add(user)
    await session.commit()
    return GenericMessageResponse(ok=True, message="Admin creado")


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    enforce_rate_limit(request, key="login")
    email = payload.email.lower().strip()
    user = await session.scalar(select(UsuarioDashboard).where(UsuarioDashboard.email == email))
    if user is None or not user.activo or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

    user.ultimo_login_at = datetime.now(timezone.utc)
    await session.commit()
    token = create_access_token(user_id=user.id, role=user.rol.value, email=user.email)
    return LoginResponse(
        access_token=token,
        user=AuthUser(id=user.id, nombre=user.nombre, apellido=user.apellido, email=user.email, rol=user.rol.value),
    )


@router.post("/users", response_model=GenericMessageResponse)
async def create_user(
    payload: CreateUserRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles("admin")),
) -> GenericMessageResponse:
    enforce_rate_limit(request, key="create-user")
    email = payload.email.lower().strip()
    exists = await session.scalar(select(UsuarioDashboard).where(UsuarioDashboard.email == email))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    # Placeholder hash; user will set final password via one-time token.
    user = UsuarioDashboard(
        nombre=payload.nombre.strip(),
        apellido=payload.apellido.strip(),
        email=email,
        rol=RolUsuario(payload.rol),
        password_hash=hash_password(generate_raw_token()),
        activo=True,
    )
    session.add(user)
    await session.flush()

    raw_token = generate_raw_token()
    token = AuthToken(
        user_id=user.id,
        token_hash=hash_raw_token(raw_token),
        tipo=TipoAuthToken.set_password,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
    )
    session.add(token)
    await session.commit()

    settings = get_settings()
    link = f"{settings.app_base_url}/user/set-password?{urlencode({'token': raw_token})}"
    await send_password_link_email(recipient=user.email, nombre=user.nombre, action="set_password", link=link)
    return GenericMessageResponse(ok=True, message="Usuario creado y enlace enviado")


@router.post("/request-password-reset", response_model=GenericMessageResponse)
async def request_password_reset(
    payload: PasswordTokenRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> GenericMessageResponse:
    enforce_rate_limit(request, key="request-reset")
    email = payload.email.lower().strip()
    user = await session.scalar(select(UsuarioDashboard).where(UsuarioDashboard.email == email))
    if user is None or not user.activo:
        return GenericMessageResponse(ok=True, message="Si el usuario existe, recibira un email")

    raw_token = generate_raw_token()
    token = AuthToken(
        user_id=user.id,
        token_hash=hash_raw_token(raw_token),
        tipo=TipoAuthToken.reset_password,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=60),
    )
    session.add(token)
    await session.commit()
    settings = get_settings()
    link = f"{settings.app_base_url}/user/set-password?{urlencode({'token': raw_token})}"
    await send_password_link_email(recipient=user.email, nombre=user.nombre, action="reset_password", link=link)
    return GenericMessageResponse(ok=True, message="Si el usuario existe, recibira un email")


@router.post("/confirm-password", response_model=GenericMessageResponse)
async def confirm_password(
    payload: ConfirmPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> GenericMessageResponse:
    enforce_rate_limit(request, key="confirm-password")
    hashed_token = hash_raw_token(payload.token)
    token = await session.scalar(select(AuthToken).where(AuthToken.token_hash == hashed_token))
    if token is None or token.used_at is not None or token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token invalido o expirado")

    user = await session.scalar(select(UsuarioDashboard).where(UsuarioDashboard.id == token.user_id))
    if user is None or not user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario invalido")

    user.password_hash = hash_password(payload.password)
    token.used_at = datetime.now(timezone.utc)
    await session.commit()
    return GenericMessageResponse(ok=True, message="Contrasena actualizada")
