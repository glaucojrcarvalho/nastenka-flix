# Nastenka Flix

Nastenka Flix is a self-hosted streaming prototype for a small private catalog. The project is split into a FastAPI backend, a Vite + React frontend, local media assets, and lightweight project documentation.

## Stack

- Backend: FastAPI, SQLAlchemy, SQLite, JWT auth
- Frontend: React, TypeScript, Vite, React Router
- Media: Local files mounted directly by the API
- Dev runtime: Docker Compose or local scripts

## Recommended Local Deployment

The repository is now set up for a single local URL on Windows, with the frontend acting as a reverse proxy for the API and media files.

### Target experience

- Open `http://nastenka-flix`
- Keep the real `.mp4` files on the same Windows laptop
- Run everything with Docker Desktop

### Windows setup

1. Install Docker Desktop for Windows.
2. Edit `C:\Windows\System32\drivers\etc\hosts` as Administrator and add:

```txt
127.0.0.1 nastenka-flix
```

3. Copy `.env.example` to `.env`.
4. Copy `backend/catalog.example.json` to `backend/catalog.json` and replace the sample series with the real catalog.
5. Put the actual video files under `media/series/...` so each `media_path` in `backend/catalog.json` matches a real file.
6. Start the app:

```powershell
.\windows\run-local.cmd -Build
```

7. Open `http://nastenka-flix`.

To make it start automatically when she signs in:

```powershell
.\windows\install-autostart.ps1
```

If you want one script that sets up the hosts entry, imports the configured series, starts Docker, builds the app, and installs autostart, use:

```cmd
.\windows\bootstrap-local.cmd
```

Edit [windows/bootstrap-local.ps1](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/bootstrap-local.ps1:1) first and adjust the series folders at the top.

If you want a faster bootstrap on Windows:

```powershell
.\windows\setup-local.ps1
```

If PowerShell blocks `.ps1` execution on that laptop, use the `.cmd` wrappers instead:

```cmd
.\windows\setup-local.cmd
```

### Expected local file layout

```txt
nastenka-flix/
  .env
  docker-compose.yml
  backend/
    catalog.json
  media/
    series/
      your-series-one/
        season-01/
          episode-01.mp4
      your-series-two/
      your-series-three/
```

### Importing a messy season folder

If the original files have names like `Ne.rodis.krasivoy.001...` or `S01.E001 (...)`, use the importer to clean them and write the matching catalog entry automatically:

```bash
python3 scripts/import_series.py \
  --source-dir "/path/to/original/folder" \
  --series-title "Моя прекрасная няня" \
  --season-number 1 \
  --mode move
```

What it does:

- detects episode numbers from the original filenames
- moves or copies the files into `media/series/<slug>/season-01/`
- renames them to a clean pattern like `s01e001.avi`
- creates or replaces the matching series entry in `backend/catalog.json`

For a safe preview first:

```bash
python3 scripts/import_series.py \
  --source-dir "/path/to/original/folder" \
  --series-title "Моя прекрасная няня" \
  --season-number 1 \
  --dry-run
```

For Windows, use the PowerShell wrapper instead:

```powershell
.\windows\import-series.ps1 `
  -SourceDir "D:\Series\Моя прекрасная няня DVDRip" `
  -SeriesTitle "Моя прекрасная няня" `
  -SeasonNumber 1 `
  -Mode move
```

There is also an editable example file:

```powershell
.\windows\import-series.example.ps1
```

If script execution is blocked:

```cmd
.\windows\import-series-example.cmd
```

### Starting and auto-starting on Windows

Use these files on her laptop:

- [windows/run-local.ps1](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/run-local.ps1:1) starts Docker Desktop if needed, waits for Docker, and runs `docker compose up -d`
- [windows/run-local.cmd](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/run-local.cmd:1) is the double-clickable wrapper
- [windows/bootstrap-local.ps1](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/bootstrap-local.ps1:1) is the one-shot first-run setup and import script
- [windows/bootstrap-local.cmd](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/bootstrap-local.cmd:1) is the double-clickable wrapper for it
- [windows/stop-local.ps1](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/stop-local.ps1:1) stops the app
- [windows/install-autostart.ps1](/home/glaucojrcarvalho/Projects/Pessoal/nastenka-flix/windows/install-autostart.ps1:1) registers a scheduled task to start the app at sign-in

Typical commands:

```powershell
.\windows\run-local.cmd -Build
.\windows\install-autostart.ps1
```

If `.ps1` execution is blocked, use:

```cmd
.\windows\install-autostart.cmd
```

After the first build, daily use should just be:

```powershell
.\windows\run-local.cmd
```

For a laptop that acts like a server, also change Windows power settings so it does not go to sleep when plugged in.

### Local networking model

- Browser -> `http://nastenka-flix`
- Nginx frontend container serves the React app
- `/api/*` and `/media/*` are proxied internally to the FastAPI backend
- The backend reads video files from the mounted `media/` folder

## Quick Start

### Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

The frontend will be available at `http://localhost` and, if you add the hosts entry, also at `http://nastenka-flix`.

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
