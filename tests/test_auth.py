import pytest

from app.auth import AuthError, authenticate


def test_auth_rejects_invalid_key() -> None:
    with pytest.raises(AuthError):
        authenticate("clave-invalida")
