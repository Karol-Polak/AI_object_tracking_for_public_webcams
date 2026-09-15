import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make `import src...` work regardless of the directory pytest is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.storage import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point src.storage.db at a throwaway SQLite file instead of the real one."""
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    test_engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setattr(db, "engine", test_engine)
    monkeypatch.setattr(db, "SessionLocal", sessionmaker(bind=test_engine))
    db.init_db()
    return test_engine
