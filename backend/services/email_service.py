from __future__ import annotations

from datetime import datetime
from email.utils import parseaddr
from pathlib import Path
from uuid import UUID

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from config import get_settings


def _build_mailer() -> FastMail:
    settings = get_settings()
    from_name, from_email = parseaddr(settings.email.remitente)
    if not from_email:
        raise ValueError("email.remitente debe tener formato valido, por ejemplo: Nombre <mail@dominio.com>")

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.email.smtp_user,
        MAIL_PASSWORD=settings.email.smtp_password,
        MAIL_FROM=from_email,
        MAIL_FROM_NAME=from_name or "Sistema Control",
        MAIL_PORT=settings.email.smtp_port,
        MAIL_SERVER=settings.email.smtp_host,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(conf)


def _build_subject(legajo: str, fecha_hora: datetime) -> str:
    return f"Control requerido - Legajo {legajo} - {fecha_hora.strftime('%d/%m/%Y %H:%M')}"


def _build_html(nombre_completo: str, legajo: str, fecha_hora: datetime) -> str:
    return (
        "<h3>Control antidrogas</h3>"
        f"<p><b>Nombre completo:</b> {nombre_completo}</p>"
        f"<p><b>Legajo:</b> {legajo}</p>"
        f"<p><b>Fecha y hora:</b> {fecha_hora.strftime('%d/%m/%Y %H:%M')}</p>"
        "<p>El empleado debe presentarse al laboratorio.</p>"
    )


async def send_registro_email(
    *,
    sorteo_id: UUID,
    legajo: str,
    nombre: str,
    apellido: str,
    fecha_hora: datetime,
    foto_path: str,
) -> None:
    settings = get_settings()
    mailer = _build_mailer()
    subject = _build_subject(legajo, fecha_hora)
    html = _build_html(f"{nombre} {apellido}", legajo, fecha_hora)
    attachment_path = Path(foto_path)
    if not attachment_path.exists():
        raise FileNotFoundError(f"No existe foto para sorteo {sorteo_id}")

    message = MessageSchema(
        subject=subject,
        recipients=settings.email.destinatarios,
        body=html,
        subtype=MessageType.html,
        attachments=[str(attachment_path)],
    )
    await mailer.send_message(message)


async def send_password_link_email(*, recipient: str, nombre: str, action: str, link: str) -> None:
    mailer = _build_mailer()
    subject = "Configuracion de acceso - Control antidrogas" if action == "set_password" else "Recuperacion de clave"
    html = (
        "<h3>Control antidrogas - Acceso</h3>"
        f"<p>Hola {nombre},</p>"
        "<p>Usa el siguiente enlace para continuar:</p>"
        f"<p><a href=\"{link}\">{link}</a></p>"
        "<p>Este enlace vence en 60 minutos y se puede usar una sola vez.</p>"
    )
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=html,
        subtype=MessageType.html,
    )
    await mailer.send_message(message)
