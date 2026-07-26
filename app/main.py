from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, AppConfig
from app.controllers import chat, health, pages, settings
from app.services.application import ApplicationServices


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.services = ApplicationServices(AppConfig.from_env())
    app.state.services.load_runtime_settings()
    yield
    app.state.services.close()


app = FastAPI(title="Nile Connect Support AI", lifespan=lifespan)
app.mount(
    "/assets",
    StaticFiles(directory=str(ROOT_DIR / "frontend_dist" / "assets"), check_dir=False),
    name="assets",
)
app.include_router(pages.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(health.router)
