import time

import pytest

from src.core.jwt import encode_token, decode_token
from src.shared.errors import TokenError


unit = pytest.mark.unit


@unit
def test_encode_and_decode_token_round_trip() -> None:
    payload = {"sub": "user-123", "role": "admin"}

    token = encode_token(payload, expires_delta=1)

    print(token)

    assert isinstance(token, str)
    assert token

    decoded = decode_token(token)

    print(decoded)

    assert decoded["sub"] == payload["sub"]
    assert decoded["role"] == payload["role"]
    assert "iat" in decoded
    assert "exp" in decoded


@unit
def test_decode_token_raises_token_error_for_invalid_token() -> None:
    invalid_token = "this.is.not.a.valid.jwt"

    with pytest.raises(TokenError):
        decode_token(invalid_token)


@unit
def test_token_expires_after_given_delta() -> None:
    payload = {"sub": "user-123"}
    token = encode_token(payload, expires_delta=0)  # expires immediately

    # small sleep to make sure exp < now
    time.sleep(1)

    with pytest.raises(TokenError):
        decode_token(token)
