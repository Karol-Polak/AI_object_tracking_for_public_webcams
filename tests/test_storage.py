from src.storage import db
from src.storage.models import Crossing


def test_init_db_creates_crossings_table(temp_db):
    assert temp_db.dialect.has_table(temp_db.connect(), "crossings")


def test_save_crossing_persists_expected_fields(temp_db):
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


def test_get_crossing_summary_returns_empty_dict_when_no_rows(temp_db):
    assert db.get_crossing_summary() == {}


def test_get_crossing_summary_groups_counts_by_class_and_direction(temp_db):
    db.save_crossing("cam-1", "car", "in")
    db.save_crossing("cam-1", "car", "in")
    db.save_crossing("cam-1", "car", "out")
    db.save_crossing("cam-1", "person", "in")

    assert db.get_crossing_summary() == {
        "car": {"in": 2, "out": 1},
        "person": {"in": 1},
    }
