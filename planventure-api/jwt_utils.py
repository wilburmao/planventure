from datetime import datetime, timedelta

import jwt

DEFAULT_ALGORITHM = 'HS256'
DEFAULT_EXPIRATION_MINUTES = 15


def create_access_token(data: dict, secret_key: str, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    payload = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=DEFAULT_EXPIRATION_MINUTES))
    payload.update({
        'iat': now,
        'exp': expire,
    })
    return jwt.encode(payload, secret_key, algorithm=DEFAULT_ALGORITHM)


def verify_access_token(token: str, secret_key: str) -> dict | None:
    """Verify and decode a JWT token, returning payload or None on failure."""
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[DEFAULT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
