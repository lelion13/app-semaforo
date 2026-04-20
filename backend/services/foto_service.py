from __future__ import annotations

import base64
from pathlib import Path
from uuid import UUID

from config import get_settings


def save_base64_photo(sorteo_id: UUID, foto_base64: str) -> str:
    settings = get_settings()
    output_dir = Path(settings.fotos.directorio)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = foto_base64.split(",", 1)[1]
    image_bytes = base64.b64decode(payload, validate=True)

    photo_path = output_dir / f"{sorteo_id}.jpg"
    photo_path.write_bytes(image_bytes)
    return str(photo_path)
