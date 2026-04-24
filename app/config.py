from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    app_name: str
    verify_token: str
    whatsapp_access_token: str
    whatsapp_phone_number_id: str
    graph_api_version: str
    database_url: str
    encryption_key: str
    admin_api_keys: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "IOMA WhatsApp Chatbot"),
        verify_token=os.getenv("VERIFY_TOKEN", "cambiar-este-token"),
        whatsapp_access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
        whatsapp_phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        graph_api_version=os.getenv("GRAPH_API_VERSION", "v22.0"),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./secure_ioma.db"),
        encryption_key=os.getenv("ENCRYPTION_KEY", ""),
        admin_api_keys=os.getenv("ADMIN_API_KEYS", "seguridad_ioma:cambiar-api-key-segura"),
    )
