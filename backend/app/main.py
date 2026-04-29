from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, episodes, progress, series
from app.core.config import get_settings
from app.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.media_root.exists():
    app.mount("/media", StaticFiles(directory=settings.media_root), name="media")

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(series.router, prefix=settings.api_prefix)
app.include_router(episodes.router, prefix=settings.api_prefix)
app.include_router(progress.router, prefix=settings.api_prefix)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
