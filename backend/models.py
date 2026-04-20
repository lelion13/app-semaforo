from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

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
