from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SorteoResponse(BaseModel):
    resultado: str
    sorteo_id: UUID


class RegistroRequest(BaseModel):
    sorteo_id: UUID
    legajo: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    foto_base64: str = Field(min_length=30)

    @field_validator("legajo")
    @classmethod
    def validate_legajo(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Legajo debe ser numerico")
        return value

    @field_validator("foto_base64")
    @classmethod
    def validate_foto(cls, value: str) -> str:
        if not value.startswith("data:image/jpeg;base64,"):
            raise ValueError("La foto debe ser JPEG base64")
        return value


class OkResponse(BaseModel):
    ok: bool


class HealthResponse(BaseModel):
    status: str
