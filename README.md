# Nastenka Flix

Nastenka Flix is a self-hosted streaming prototype for a small private catalog. The project is split into a FastAPI backend, a Vite + React frontend, local media assets, and lightweight project documentation.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite, JWT auth
- Frontend: React, TypeScript, Vite, React Router
- Media: Local files mounted directly by the API
- Dev runtime: Docker Compose or local scripts

## Quick Start

### Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost:5173`.

The backend database is stored in the named Docker volume `backend-data`, and the media library is mounted from the local `media/` directory.

If you prefer a helper script, run `./scripts/dev.sh` or `./scripts/dev.sh -d`.

### Local development

1. Copy `.env.example` to `.env`.
2. Start the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

3. Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

4. Seed the demo data:

```bash
./scripts/seed.sh
```

## Demo Credentials

Set `DEMO_USERNAME` and `DEMO_PASSWORD` in your `.env` file (see `.env.example`).

## Project Layout

- `backend/`: API, database models, business services
- `frontend/`: SPA client for browsing and playback
- `media/`: local media library mounted by the backend
- `scripts/`: helper scripts for development workflows

## Catalog

The catalog is loaded from `backend/catalog.json` at startup (gitignored). Copy `backend/catalog.example.json` to `backend/catalog.json` and fill in your series data.

## Notes

The repository includes placeholder media paths under `media/`. Replace them with real video assets in a private environment before using the player for actual playback.
