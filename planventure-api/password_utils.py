import base64
import hashlib
import secrets

DEFAULT_ALGORITHM = 'sha256'
DEFAULT_ITERATIONS = 100_000


def generate_salt(length: int = 16) -> str:
    """Generate a cryptographically secure salt."""
    return secrets.token_hex(length)


def hash_password(password: str, salt: str | None = None, iterations: int = DEFAULT_ITERATIONS) -> str:
    """Hash a password with PBKDF2 and a unique salt."""
    if salt is None:
        salt = generate_salt()
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    dk = hashlib.pbkdf2_hmac(DEFAULT_ALGORITHM, password_bytes, salt_bytes, iterations)
    hashed = base64.urlsafe_b64encode(dk).decode('ascii').rstrip('=')
    return f'pbkdf2_{DEFAULT_ALGORITHM}${iterations}${salt}${hashed}'


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        algorithm, iterations, salt, encoded_hash = stored_hash.split('$', 3)
        if not algorithm.startswith('pbkdf2_'):
            return False
        algorithm = algorithm.split('_', 1)[1]
        iterations = int(iterations)
    except ValueError:
        return False

    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    dk = hashlib.pbkdf2_hmac(algorithm, password_bytes, salt_bytes, iterations)
    expected_hash = base64.urlsafe_b64encode(dk).decode('ascii').rstrip('=')
    return secrets.compare_digest(expected_hash, encoded_hash)
