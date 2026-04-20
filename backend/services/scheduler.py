from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from config import get_settings
from database import SessionLocal
from models import RegistroRojo
from services.email_service import send_registro_email

scheduler = AsyncIOScheduler()


async def retry_pending_emails() -> None:
    settings = get_settings()
    async with SessionLocal() as session:
        stmt = (
            select(RegistroRojo)
            .where(RegistroRojo.email_enviado.is_(False))
            .where(RegistroRojo.email_error.is_not(None))
        )
        registros = (await session.scalars(stmt)).all()

        for registro in registros:
            if registro.email_intentos >= settings.email_reintentos.max_intentos:
                registro.email_error = "MAX_INTENTOS_SUPERADOS"
                continue

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
                registro.email_intentos = registro.email_intentos + 1
                if registro.email_intentos >= settings.email_reintentos.max_intentos:
                    registro.email_error = "MAX_INTENTOS_SUPERADOS"
                else:
                    registro.email_error = str(exc)[:1000]

        await session.commit()


def start_scheduler() -> None:
    settings = get_settings()
    if scheduler.running:
        return
    scheduler.add_job(
        retry_pending_emails,
        trigger="interval",
        minutes=settings.email_reintentos.intervalo_minutos,
        id="retry_emails",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
