from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from models import RegistroRojo
from schemas import DashboardRegistroResponse, DashboardResumenResponse, UpdateDashboardRegistroRequest
from security import require_roles

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/registros", response_model=list[DashboardRegistroResponse])
async def list_registros(
    estado: str | None = Query(default=None, pattern="^(pendiente|realizado|no_asistio)$"),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles("admin", "rrhh")),
) -> list[DashboardRegistroResponse]:
    stmt = select(RegistroRojo).order_by(RegistroRojo.fecha_hora.desc()).limit(200)
    if estado:
        stmt = stmt.where(RegistroRojo.estado_control == estado)
    if q:
        like_term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                RegistroRojo.legajo.ilike(like_term),
                RegistroRojo.nombre.ilike(like_term),
                RegistroRojo.apellido.ilike(like_term),
            )
        )

    registros = (await session.scalars(stmt)).all()
    return [
        DashboardRegistroResponse(
            id=item.id,
            sorteo_id=item.sorteo_id,
            legajo=item.legajo,
            nombre=item.nombre,
            apellido=item.apellido,
            fecha_hora=item.fecha_hora.isoformat(),
            email_enviado=item.email_enviado,
            email_intentos=item.email_intentos,
            email_error=item.email_error,
            estado_control=item.estado_control,
            fecha_control=item.fecha_control.isoformat() if item.fecha_control else None,
            observacion_control=item.observacion_control,
        )
        for item in registros
    ]


@router.patch("/registros/{registro_id}", response_model=DashboardRegistroResponse)
async def update_registro(
    registro_id: str,
    payload: UpdateDashboardRegistroRequest,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles("admin", "rrhh")),
) -> DashboardRegistroResponse:
    registro = await session.scalar(select(RegistroRojo).where(RegistroRojo.id == registro_id))
    if registro is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")

    registro.estado_control = payload.estado_control
    registro.observacion_control = payload.observacion_control
    registro.fecha_control = datetime.now(timezone.utc) if payload.estado_control == "realizado" else None
    await session.commit()
    await session.refresh(registro)
    return DashboardRegistroResponse(
        id=registro.id,
        sorteo_id=registro.sorteo_id,
        legajo=registro.legajo,
        nombre=registro.nombre,
        apellido=registro.apellido,
        fecha_hora=registro.fecha_hora.isoformat(),
        email_enviado=registro.email_enviado,
        email_intentos=registro.email_intentos,
        email_error=registro.email_error,
        estado_control=registro.estado_control,
        fecha_control=registro.fecha_control.isoformat() if registro.fecha_control else None,
        observacion_control=registro.observacion_control,
    )


@router.get("/resumen", response_model=DashboardResumenResponse)
async def resumen(
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles("admin", "rrhh")),
) -> DashboardResumenResponse:
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    positivos_hoy = await session.scalar(
        select(func.count())
        .select_from(RegistroRojo)
        .where(RegistroRojo.fecha_hora >= day_start, RegistroRojo.fecha_hora < day_end)
    )
    pendientes = await session.scalar(
        select(func.count()).select_from(RegistroRojo).where(RegistroRojo.estado_control == "pendiente")
    )
    return DashboardResumenResponse(positivos_hoy=int(positivos_hoy or 0), pendientes=int(pendientes or 0))


@router.get("/registros/{registro_id}/foto")
async def get_registro_photo(
    registro_id: str,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_roles("admin", "rrhh")),
) -> FileResponse:
    registro = await session.scalar(select(RegistroRojo).where(RegistroRojo.id == registro_id))
    if registro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado")
    if not registro.foto_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto no disponible")

    photo_path = Path(registro.foto_path)
    if not photo_path.exists() or not photo_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo de foto no encontrado")

    response = FileResponse(path=str(photo_path), media_type="image/jpeg", filename=f"{registro.sorteo_id}.jpg")
    response.headers["Cache-Control"] = "no-store"
    return response
