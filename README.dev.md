# Dev Guide

Detailed setup and workflow for local development.

## Requirements

- Python 3.12+
- `pip`
- Linux/macOS/WSL (commands below use POSIX shell)

## 1. Clone and Enter Project

```bash
git clone https://github.com/vasili-sikora/DL2026_Spring_FSD_Sikora
cd DL2026_Spring_FSD_Sikora
```

## 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Environment

```bash
cp .env.example .env
```

Recommended local values:

- `DB_PATH=data/app.db`
- `SESSION_SECRET_KEY=<random-secret>`
- `SESSION_COOKIE_SECURE=false` (local HTTP)

## 4. Apply Migrations

```bash
.venv/bin/alembic current
.venv/bin/alembic upgrade head
```

## 5. Run App

```bash
.venv/bin/uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open: http://127.0.0.1:8000

## 6. Testing

Run all tests:

```bash
.venv/bin/pytest -q
```

Run one test module:

```bash
.venv/bin/pytest tests/test_generated_images_service.py -q
```

## 7. Admin User Management

Promote existing user:

```bash
.venv/bin/python -m app.backend.scripts.manage_admin --email you@example.com
```

Create new admin if user does not exist:

```bash
.venv/bin/python -m app.backend.scripts.manage_admin --email you@example.com --password "StrongPass123"
```

## 8. Public Demo Tunnel

Using Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

## 9. Troubleshooting

- `503` in tunnel:
  Backend is not running on `127.0.0.1:8000`.

- Login/session does not persist over HTTPS tunnel:
  set `SESSION_COOKIE_SECURE=true` in `.env` and restart app.

- Migration mismatch:

```bash
.venv/bin/alembic current
.venv/bin/alembic history
```

## 10. Backend Layout

- `app/backend/api` - HTTP routes
- `app/backend/services` - business logic
- `app/backend/repositories` - database queries
- `app/backend/models` - Pydantic request/response schemas
- `app/backend/auth` - session and auth dependencies
- `app/backend/storage` - file path and upload helpers
