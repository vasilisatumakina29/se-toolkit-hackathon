import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database import Base, SessionLocal, engine
from app.routers import api, pages


def init_db(max_attempts: int = 10, delay_seconds: int = 2) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="LostLink", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(api.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/about", response_class=HTMLResponse, tags=["pages"])
def about() -> str:
    return "<h2>LostLink</h2><p>A campus lost and found web app.</p>"
