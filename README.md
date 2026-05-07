# PlanVenture API 🚀

A Flask-based REST API backend for the PlanVenture application.

This service provides user authentication, JWT token handling, and trip management for a React frontend.

---

## Features

- Flask REST API with `flask_sqlalchemy`
- User registration and login via email/password
- Secure password hashing with PBKDF2
- JWT authentication for protected routes
- Trip CRUD operations scoped to the authenticated user
- Default itinerary template generation when none is provided
- CORS support for React development on `localhost:3000`
- SQLite persistence for simple local development

---

## Requirements

- Python 3.10+ (tested with Python 3.12)
- `pip`
- `virtualenv` or built-in `venv`

---

## Project Structure

```text
planventure/
  README.md
  LICENSE
  planventure-api/
    app.py
    auth.py
    database.py
    jwt_utils.py
    models.py
    password_utils.py
    trips.py
    create_db.py
    requirements.txt
    .env.example
    planventure.db
```

---

## Setup

```sh
cd planventure-api
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from the example:

```sh
copy .env.example .env
```

Then update `.env` as needed.

---

## Environment Variables

The API supports these environment variables:

- `SECRET_KEY` - Flask secret key and JWT signing key
- `DATABASE_URL` - SQLAlchemy database URI
- `CORS_ORIGINS` - comma-separated allowed origins for CORS

Example `.env`:

```env
FLASK_ENV=development
SECRET_KEY=replace-with-a-strong-secret-key
DATABASE_URL=sqlite:///planventure.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Run the API

```sh
flask run
```

Or with Python directly:

```sh
python app.py
```

---

## Database Initialization

The app automatically creates missing tables on startup. If needed, run:

```sh
python create_db.py
```

---

## API Endpoints

### Public

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /db-status` - Database connectivity check

### Authentication

#### Register

`POST /auth/register`

Request JSON:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:

```json
{
  "message": "User registered successfully.",
  "token": "<jwt-token>"
}
```

#### Login

`POST /auth/login`

Request JSON:

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response:

```json
{
  "message": "Login successful.",
  "token": "<jwt-token>",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

#### Current user

`GET /auth/me`

Headers:

```http
Authorization: Bearer <jwt-token>
```

Response:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### Trips

All trip routes require the `Authorization` header:

```http
Authorization: Bearer <jwt-token>
```

#### List trips

`GET /trips`

#### Create trip

`POST /trips`

Request JSON:

```json
{
  "destination": "Paris, France",
  "start_date": "2026-07-01",
  "end_date": "2026-07-10",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "itinerary": "Day 1: Louvre, Day 2: Eiffel Tower"
}
```

If `itinerary` is omitted, the API generates a default itinerary template.

Response:

```json
{
  "message": "Trip created successfully.",
  "trip_id": 1
}
```

#### Get a trip

`GET /trips/<trip_id>`

#### Update a trip

`PUT /trips/<trip_id>`

#### Delete a trip

`DELETE /trips/<trip_id>`

---

## CORS

The API is configured to allow requests from React development hosts by default:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

Use `CORS_ORIGINS` to customize allowed origins.

---

## Notes

- Passwords are hashed using PBKDF2 with random salt.
- JWT tokens are signed with `HS256` and the `SECRET_KEY`.
- Trip data is scoped per user via `user_id`.
- Existing SQLite table schema changes are handled safely on startup.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
