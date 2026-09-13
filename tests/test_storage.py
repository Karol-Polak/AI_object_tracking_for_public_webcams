from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config
from src.storage import db
from src.storage.models import Crossing


def _use_temp_database(monkeypatch, tmp_path):
    """Point src.storage.db at a throwaway SQLite file instead of the real one."""
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    test_engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setattr(db, "engine", test_engine)
    monkeypatch.setattr(db, "SessionLocal", sessionmaker(bind=test_engine))
    return test_engine


def test_init_db_creates_crossings_table(tmp_path, monkeypatch):
    test_engine = _use_temp_database(monkeypatch, tmp_path)

    db.init_db()

    assert test_engine.dialect.has_table(test_engine.connect(), "crossings")


def test_save_crossing_persists_expected_fields(tmp_path, monkeypatch):
    _use_temp_database(monkeypatch, tmp_path)
    db.init_db()

    db.save_crossing("camera-1", "car", "in")

    session = db.SessionLocal()
    try:
        rows = session.query(Crossing).all()
    finally:
        session.close()

    assert len(rows) == 1
    assert rows[0].camera_id == "camera-1"
    assert rows[0].object_class == "car"
    assert rows[0].direction == "in"
    assert rows[0].timestamp is not None
