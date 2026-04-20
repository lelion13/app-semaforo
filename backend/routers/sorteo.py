from __future__ import annotations

import secrets
import uuid

from fastapi import APIRouter

from config import get_settings
from schemas import SorteoResponse

router = APIRouter(prefix="/api", tags=["sorteo"])


@router.post("/sorteo", response_model=SorteoResponse)
async def crear_sorteo() -> SorteoResponse:
    settings = get_settings()
    numero = secrets.randbelow(100)
    resultado = "rojo" if numero < settings.sorteo.probabilidad_rojo else "verde"
    return SorteoResponse(resultado=resultado, sorteo_id=uuid.uuid4())
