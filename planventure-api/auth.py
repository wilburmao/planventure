from functools import wraps

from flask import current_app, jsonify, request

from jwt_utils import verify_access_token
from models import User


def _get_bearer_token() -> str | None:
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return None


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = _get_bearer_token()
        if not token:
            return jsonify({'error': 'Authorization header required.'}), 401

        payload = verify_access_token(token, current_app.config['SECRET_KEY'])
        if not payload:
            return jsonify({'error': 'Invalid or expired token.'}), 401

        user_id = payload.get('user_id')
        if not user_id:
            return jsonify({'error': 'Invalid token payload.'}), 401

        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': 'User not found.'}), 401

        return func(current_user=user, token_payload=payload, *args, **kwargs)

    return wrapper
