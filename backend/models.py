from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class RegistroRojo(Base):
    __tablename__ = "registros_rojos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()")
    )
    sorteo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    legajo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    foto_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    email_enviado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    email_intentos: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    email_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado_control: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pendiente'"))
    fecha_control: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observacion_control: Mapped[str | None] = mapped_column(Text, nullable=True)


class RolUsuario(str, Enum):
    admin = "admin"
    rrhh = "rrhh"


class TipoAuthToken(str, Enum):
    set_password = "set_password"
    reset_password = "reset_password"


class UsuarioDashboard(Base):
    __tablename__ = "usuarios_dashboard"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()")
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    rol: Mapped[RolUsuario] = mapped_column(SqlEnum(RolUsuario, name="rol_usuario"), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    ultimo_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), onupdate=datetime.utcnow
    )

    tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios_dashboard.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tipo: Mapped[TipoAuthToken] = mapped_column(SqlEnum(TipoAuthToken, name="tipo_auth_token"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user: Mapped[UsuarioDashboard] = relationship(back_populates="tokens")
