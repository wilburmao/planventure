import os
import re
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from database import db
from jwt_utils import create_access_token
from auth import token_required
from models import User

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'planventure-secret-key'),
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{BASE_DIR / 'planventure.db'}"
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


@app.route('/auth/register', methods=['POST'])
def register_user():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get('email', '')).strip().lower()
    password = str(payload.get('password', ''))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format."}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email is already registered."}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
    }, app.config['SECRET_KEY'])

    return jsonify({
        "message": "User registered successfully.",
        "token": token,
    }), 201


@app.route('/auth/login', methods=['POST'])
def login_user():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get('email', '')).strip().lower()
    password = str(payload.get('password', ''))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
    }, app.config['SECRET_KEY'])

    return jsonify({
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
        },
    }), 200


@app.route('/auth/me')
@token_required
def get_current_user(current_user, token_payload):
    return jsonify({
        "user": {
            "id": current_user.id,
            "email": current_user.email,
        }
    }), 200


@app.route('/db-status')
def db_status():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"database": "connected"})
    except Exception as exc:
        return jsonify({"database": "error", "message": str(exc)}), 500


if __name__ == '__main__':
    app.run(debug=True)
