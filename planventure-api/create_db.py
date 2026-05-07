from app import app
from database import db


def create_database():
    with app.app_context():
        db.create_all()
        print('Database tables created successfully.')


if __name__ == '__main__':
    create_database()
