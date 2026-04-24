from __future__ import annotations

from dataclasses import dataclass
import hmac

from app.config import get_settings


@dataclass
class Actor:
    actor_id: str
    role: str = "authorized_staff"


class AuthError(Exception):
    pass


def parse_api_keys() -> dict[str, str]:
    settings = get_settings()
    pairs = [p.strip() for p in settings.admin_api_keys.split(",") if p.strip()]
    result: dict[str, str] = {}
    for pair in pairs:
        if ":" not in pair:
            continue
        actor, key = pair.split(":", 1)
        result[actor.strip()] = key.strip()
    return result


def _safe_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def authenticate(api_key: str | None) -> Actor:
    if not api_key:
        raise AuthError("Falta X-API-Key")

    for actor, valid_key in parse_api_keys().items():
        if _safe_equal(api_key, valid_key):
            return Actor(actor_id=actor)
    raise AuthError("API key inválida")
