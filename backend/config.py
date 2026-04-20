from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


def _parse_frontend_urls() -> list[str]:
    """Orígenes CORS: FRONTEND_URLS (coma) o FRONTEND_URL (compatibilidad)."""
    raw_list = os.getenv("FRONTEND_URLS", "").strip()
    if raw_list:
        urls = [u.strip() for u in raw_list.split(",") if u.strip()]
        if not urls:
            raise ValueError("FRONTEND_URLS no contiene orígenes válidos")
        return urls
    single = os.getenv("FRONTEND_URL", "").strip()
    if not single:
        raise ValueError("FRONTEND_URL o FRONTEND_URLS es requerido")
    return [single]


@dataclass(frozen=True)
class SorteoConfig:
    probabilidad_rojo: int


@dataclass(frozen=True)
class EmailConfig:
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    remitente: str
    destinatarios: list[str]


@dataclass(frozen=True)
class EmpresaConfig:
    nombre: str
    logo_url: str


@dataclass(frozen=True)
class FotosConfig:
    directorio: str


@dataclass(frozen=True)
class EmailReintentosConfig:
    intervalo_minutos: int
    max_intentos: int


@dataclass(frozen=True)
class Settings:
    database_url: str
    api_key: str
    frontend_urls: list[str]
    sorteo: SorteoConfig
    email: EmailConfig
    empresa: EmpresaConfig
    fotos: FotosConfig
    email_reintentos: EmailReintentosConfig


def _load_yaml(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    if not isinstance(raw, dict):
        raise ValueError("config.yaml invalido")
    return raw


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    config_path = Path(__file__).parent / "config.yaml"
    yaml_config = _load_yaml(config_path)

    database_url = os.getenv("DATABASE_URL", "")
    api_key = os.getenv("API_KEY", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")

    if not database_url:
        raise ValueError("DATABASE_URL es requerido")
    if not api_key:
        raise ValueError("API_KEY es requerido")
    if len(api_key) < 32:
        raise ValueError("API_KEY debe tener al menos 32 caracteres")
    frontend_urls = _parse_frontend_urls()

    email_yaml = yaml_config.get("email", {})
    smtp_password = email_password or str(email_yaml.get("smtp_password", ""))
    if not smtp_password:
        raise ValueError("EMAIL_PASSWORD es requerido")

    sorteo_cfg = SorteoConfig(probabilidad_rojo=int(yaml_config["sorteo"]["probabilidad_rojo"]))
    if sorteo_cfg.probabilidad_rojo < 0 or sorteo_cfg.probabilidad_rojo > 100:
        raise ValueError("sorteo.probabilidad_rojo debe estar entre 0 y 100")

    email_cfg = EmailConfig(
        smtp_host=str(email_yaml["smtp_host"]),
        smtp_port=int(email_yaml["smtp_port"]),
        smtp_user=str(email_yaml["smtp_user"]),
        smtp_password=smtp_password,
        remitente=str(email_yaml["remitente"]),
        destinatarios=[str(item) for item in email_yaml.get("destinatarios", [])],
    )
    if not email_cfg.destinatarios:
        raise ValueError("email.destinatarios no puede estar vacio")

    empresa_yaml = yaml_config.get("empresa", {})
    empresa_cfg = EmpresaConfig(
        nombre=str(empresa_yaml.get("nombre", "Empresa")),
        logo_url=str(empresa_yaml.get("logo_url", "")),
    )

    fotos_yaml = yaml_config.get("fotos", {})
    fotos_cfg = FotosConfig(directorio=str(fotos_yaml.get("directorio", "./fotos")))

    reintentos_yaml = yaml_config.get("email_reintentos", {})
    reintentos_cfg = EmailReintentosConfig(
        intervalo_minutos=int(reintentos_yaml.get("intervalo_minutos", 5)),
        max_intentos=int(reintentos_yaml.get("max_intentos", 5)),
    )

    return Settings(
        database_url=database_url,
        api_key=api_key,
        frontend_urls=frontend_urls,
        sorteo=sorteo_cfg,
        email=email_cfg,
        empresa=empresa_cfg,
        fotos=fotos_cfg,
        email_reintentos=reintentos_cfg,
    )
