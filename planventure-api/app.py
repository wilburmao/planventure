import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from database import db
from models import User

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

@app.route('/db-status')
def db_status():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"database": "connected"})
    except Exception as exc:
        return jsonify({"database": "error", "message": str(exc)}), 500

if __name__ == '__main__':
    app.run(debug=True)
