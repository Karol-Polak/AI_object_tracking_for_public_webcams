"""
Database engine/session setup and helper functions for storage.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.storage.models import Base, Crossing
from src import config

DB_PATH = config.DATA_DIR / "tracker.db"

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create tables if they don't exist yet."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)


def save_crossing(camera_id: str, object_class: str, direction: str):
    session = SessionLocal()
    try:
        crossing = Crossing(camera_id=camera_id, object_class=object_class, direction=direction)
        session.add(crossing)
        session.commit()
    finally:
        session.close()