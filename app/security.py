from __future__ import annotations

import base64
import hashlib
import hmac
import os
from cryptography.fernet import Fernet

from app.config import get_settings


def get_or_create_encryption_key() -> bytes:
    settings = get_settings()
    if settings.encryption_key:
        return settings.encryption_key.encode("utf-8")

    # fallback local para desarrollo; en producción debe venir de un KMS/HSM
    key_path = ".local_fernet.key"
    if os.path.exists(key_path):
        return open(key_path, "rb").read().strip()

    key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(key)
    return key


def get_fernet() -> Fernet:
    return Fernet(get_or_create_encryption_key())


def encrypt_value(value: str) -> str:
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(value: str) -> str:
    return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")


def hash_value(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8")


def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
