from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


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


class BootstrapStatusResponse(BaseModel):
    needs_bootstrap: bool


class BootstrapAdminRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthUser(BaseModel):
    id: UUID
    nombre: str
    apellido: str
    email: EmailStr
    rol: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class CreateUserRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    email: EmailStr
    rol: str = Field(pattern="^(admin|rrhh)$")


class GenericMessageResponse(BaseModel):
    ok: bool
    message: str


class PasswordTokenRequest(BaseModel):
    email: EmailStr


class ConfirmPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    password: str = Field(min_length=10, max_length=128)


class DashboardRegistroResponse(BaseModel):
    id: UUID
    sorteo_id: UUID
    legajo: str
    nombre: str
    apellido: str
    fecha_hora: str
    email_enviado: bool
    email_intentos: int
    email_error: str | None
    estado_control: str
    fecha_control: str | None
    observacion_control: str | None


class UpdateDashboardRegistroRequest(BaseModel):
    estado_control: str = Field(pattern="^(pendiente|realizado|no_asistio)$")
    observacion_control: str | None = Field(default=None, max_length=1000)


class DashboardResumenResponse(BaseModel):
    positivos_hoy: int
    pendientes: int
