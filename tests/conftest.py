from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config as app_config
from app import database, main


@pytest.fixture
def client_and_sessionmaker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path.as_posix()}"

    monkeypatch.setattr(app_config.settings, "database_url", database_url)

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", session_local)
    monkeypatch.setattr(main, "SessionLocal", session_local)

    database.run_migrations()

    with TestClient(main.app) as client:
        yield client, session_local

    engine.dispose()
