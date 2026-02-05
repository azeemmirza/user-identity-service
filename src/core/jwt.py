import datetime as dt

from jose import jwt, JWTError

from src.core.config import get_config
from src.shared.errors import TokenError


_config = get_config()


def encode_token(payload: dict, expires_delta: int | None = None) -> str:
    """Encode a JWT with optional expiration in minutes."""
    iat = dt.datetime.now(dt.timezone.utc)
    if expires_delta is not None:
        exp = iat + dt.timedelta(minutes=expires_delta)
        payload = {**payload, 'iat': int(iat.timestamp()), 'exp': int(exp.timestamp())}
    else:
        payload = {**payload, 'iat': int(iat.timestamp())}

    return jwt.encode(
        payload,
        _config.JWT_SECRET,
        algorithm=_config.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    """Decode a JWT and return its payload, raising TokenError on failure."""
    try:
        return jwt.decode(
            token,
            _config.JWT_SECRET,
            algorithms=[_config.JWT_ALGORITHM],
        )
    except JWTError as e:
        raise TokenError(str(e)) from e
