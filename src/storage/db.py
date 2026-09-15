"""
Database engine/session setup and helper functions for storage.
"""

from sqlalchemy import create_engine, func
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


def get_crossing_summary() -> dict:
    """Aggregate crossing counts, grouped by object_class then direction.

    Returns e.g. {"car": {"in": 3, "out": 1}}. Empty dict if there are no
    rows yet.
    """
    session = SessionLocal()
    try:
        rows = (
            session.query(Crossing.object_class, Crossing.direction, func.count(Crossing.id))
            .group_by(Crossing.object_class, Crossing.direction)
            .all()
        )
    finally:
        session.close()

    summary: dict = {}
    for object_class, direction, count in rows:
        summary.setdefault(object_class, {})[direction] = count
    return summary