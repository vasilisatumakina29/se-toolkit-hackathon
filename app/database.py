from pathlib import Path
from collections.abc import Generator
from typing import Any

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs(db_url: str) -> dict[str, Any]:
    if db_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _alembic_config() -> Config:
    config = Config(str(_project_root() / "alembic.ini"))
    config.set_main_option("script_location", str(_project_root() / "alembic"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    return config


def run_migrations() -> None:
    config = _alembic_config()
    inspector = inspect(engine)

    if inspector.has_table("items") and not inspector.has_table("alembic_version"):
        command.stamp(config, "0001_create_items_table")

    command.upgrade(config, "head")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
