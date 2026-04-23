from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = "IOMA WhatsApp Chatbot"
    verify_token: str = Field(default="cambiar-este-token")
    whatsapp_access_token: str = Field(default="")
    whatsapp_phone_number_id: str = Field(default="")
    graph_api_version: str = Field(default="v22.0")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
