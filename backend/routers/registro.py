from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from models import RegistroRojo
from schemas import OkResponse, RegistroRequest
from services.email_service import send_registro_email
from services.foto_service import save_base64_photo

router = APIRouter(prefix="/api", tags=["registro"])


@router.post("/registro", response_model=OkResponse)
async def crear_registro(
    payload: RegistroRequest,
    session: AsyncSession = Depends(get_db_session),
) -> OkResponse:
    existing = await session.scalar(select(RegistroRojo).where(RegistroRojo.sorteo_id == payload.sorteo_id))
    if existing is not None:
        return OkResponse(ok=True)

    try:
        foto_path = save_base64_photo(payload.sorteo_id, payload.foto_base64)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Foto invalida") from exc

    now = datetime.now(timezone.utc)
    registro = RegistroRojo(
        sorteo_id=payload.sorteo_id,
        legajo=payload.legajo,
        nombre=payload.nombre,
        apellido=payload.apellido,
        foto_path=foto_path,
        fecha_hora=now,
        email_enviado=False,
        email_intentos=0,
        email_error=None,
    )
    session.add(registro)
    await session.flush()

    try:
        await send_registro_email(
            sorteo_id=registro.sorteo_id,
            legajo=registro.legajo,
            nombre=registro.nombre,
            apellido=registro.apellido,
            fecha_hora=registro.fecha_hora,
            foto_path=registro.foto_path or "",
        )
        registro.email_enviado = True
        registro.email_error = None
    except Exception as exc:  # noqa: BLE001
        registro.email_enviado = False
        registro.email_intentos = 1
        registro.email_error = str(exc)[:1000]

    await session.commit()
    return OkResponse(ok=True)
