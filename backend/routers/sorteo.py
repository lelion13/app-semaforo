from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db_session
from models import RegistroRojo
from schemas import SorteoResponse

router = APIRouter(prefix="/api", tags=["sorteo"])


@router.post("/sorteo", response_model=SorteoResponse)
async def crear_sorteo(session: AsyncSession = Depends(get_db_session)) -> SorteoResponse:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    rojos_hoy = await session.scalar(
        select(func.count())
        .select_from(RegistroRojo)
        .where(RegistroRojo.fecha_hora >= day_start, RegistroRojo.fecha_hora < day_end)
    )
    rojos_hoy = int(rojos_hoy or 0)

    if rojos_hoy >= settings.sorteo.max_rojos_dia:
        return SorteoResponse(resultado="verde", sorteo_id=uuid.uuid4())

    numero = secrets.randbelow(100)
    resultado = "rojo" if numero < settings.sorteo.probabilidad_rojo else "verde"
    return SorteoResponse(resultado=resultado, sorteo_id=uuid.uuid4())
