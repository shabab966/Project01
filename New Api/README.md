# Sign-In API

A small REST API with **username/password sign-in** built on **Flask**,
**Flask-Login**, and **SQLite**. Authentication uses server-side sessions
(signed cookies) — no tokens required.

## Stack

- **Python 3.13** + **Flask 3**
- **Flask-Login** for session-based authentication
- **Werkzeug** for secure password hashing (`pbkdf2`/`scrypt`)
- **SQLite** for user storage (`app.db`, created automatically)

## Quick start

```bash
# 1. (optional) create a virtual environment
python -m venv .venv
source .venv/Scripts/activate    # Git Bash on Windows

# 2. install dependencies
python -m pip install -r requirements.txt

# 3. run the server
python app.py
```

The API starts at **http://127.0.0.1:5000**.

## API endpoints

All auth routes are under `/api/auth`. JSON request/response.

| Method | Endpoint              | Auth? | Description                          |
|--------|-----------------------|-------|--------------------------------------|
| GET    | `/`                   | no    | Lists all endpoints                  |
| POST   | `/api/auth/register`  | no    | Create account + sign in             |
| POST   | `/api/auth/login`     | no    | Sign in with username & password     |
| POST   | `/api/auth/logout`    | yes   | End session                          |
| GET    | `/api/auth/me`        | yes   | Current signed-in user               |
| GET    | `/api/protected`      | yes   | Example protected route              |

### Register

```bash
curl -c cookies.txt -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secret123"}'
```

### Login

```bash
curl -c cookies.txt -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secret123"}'
```

### Access a protected route

The session cookie (`-b cookies.txt`) is what authenticates you:

```bash
curl -b cookies.txt http://127.0.0.1:5000/api/protected
```

### Logout

```bash
curl -b cookies.txt -X POST http://127.0.0.1:5000/api/auth/logout
```

## Validation rules

- `username`: at least 3 characters, must be unique.
- `password`: at least 6 characters.
- Login failures return a generic `"Invalid username or password."` so valid
  usernames can't be discovered.

## Project layout

```
New Api/
├── app.py            # App factory, Flask-Login setup, /api/protected route
├── auth.py           # Auth blueprint: register, login, logout, me
├── models.py         # User model (password hashing + DB persistence)
├── db.py             # SQLite connection helpers + schema
├── config.py         # Settings (DB path, secret key, cookie flags)
├── requirements.txt
└── README.md
```

`app.db` is created automatically on first request.

## Security notes for production

This is a development setup. Before deploying:

1. **Set a real secret key** — `export APP_SECRET_KEY="a-long-random-string"`.
2. **Serve over HTTPS** and enable `SESSION_COOKIE_SECURE = True` in
   `config.py` so cookies are only sent over HTTPS.
3. Run behind a production WSGI server (`gunicorn`/`waitress`), not Flask's
   dev server (`app.run`).
4. Consider rate-limiting the login endpoint to slow brute-force attempts.
