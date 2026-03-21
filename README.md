# DevCraft Meme Studio

Template-based image generator on FastAPI with cookie auth and a built-in frontend.

## Features

- User registration and login
- Template catalog
- Image generation from templates
- User-bound generated images
- Admin template management

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.backend.main:app --host 127.0.0.1 --port 8000
```

Open: http://127.0.0.1:8000

## Run Tests

```bash
.venv/bin/pytest -q
```

## Developer Documentation

Detailed developer guide is available in [README.dev.md](README.dev.md).

## Project Structure

- `app/backend/main.py` - FastAPI app entry point
- `app/backend/api/` - API routes
- `app/backend/services/` - business logic
- `app/backend/repositories/` - DB access layer
- `app/backend/models/` - Pydantic schemas
- `alembic/` - DB migrations
- `app/frontend/` - static frontend
