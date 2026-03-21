# DevCraft Meme Studio

FastAPI application for template-based image generation with:
- user auth (cookie session)
- template catalog and admin template management
- generated images linked to the current user
- static frontend served from the same app

## Requirements

- Python 3.12+
- `pip`
- Linux/macOS/WSL (commands below are POSIX shell)

## 1. Clone and enter project

```bash
git clone https://github.com/vasili-sikora/DL2026_Spring_FSD_Sikora
cd DL2026_Spring_FSD_Sikora
```

## 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure environment

```bash
cp .env.example .env
```

Minimal local setup from `.env`:
- `DB_PATH=data/app.db`
- `SESSION_SECRET_KEY=<random-secret>`
- `SESSION_COOKIE_SECURE=false` (for local HTTP)

## 4. Run database migrations

```bash
.venv/bin/alembic upgrade head
```

## 5. Start application

```bash
.venv/bin/uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open in browser:
- http://127.0.0.1:8000

## Useful commands

### Create or promote admin user

```bash
# Promote existing user
.venv/bin/python -m app.backend.scripts.manage_admin --email you@example.com

# Or create new admin if user does not exist
.venv/bin/python -m app.backend.scripts.manage_admin --email you@example.com --password 'StrongPass123'
```

## Project structure 

- `app/backend/main.py` - FastAPI app entry point
- `app/backend/api/` - HTTP routes
- `app/backend/services/` - business logic
- `app/backend/repositories/` - DB queries
- `app/backend/models/` - Pydantic request/response models
- `alembic/` - DB migrations
- `app/frontend/` - static frontend
