from src.storage import db
from src.dashboard.app import create_app


def test_api_summary_returns_empty_object_for_empty_database(temp_db):
    client = create_app().test_client()

    response = client.get("/api/summary")

    assert response.status_code == 200
    assert response.get_json() == {}


def test_api_summary_returns_seeded_counts(temp_db):
    db.save_crossing("cam-1", "car", "in")
    db.save_crossing("cam-1", "car", "in")
    db.save_crossing("cam-1", "person", "out")
    client = create_app().test_client()

    response = client.get("/api/summary")

    assert response.status_code == 200
    assert response.get_json() == {"car": {"in": 2}, "person": {"out": 1}}


def test_index_returns_200_and_renders_counts(temp_db):
    db.save_crossing("cam-1", "car", "in")
    db.save_crossing("cam-1", "car", "in")
    db.save_crossing("cam-1", "person", "out")
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Crossings Dashboard" in body
    assert "car" in body


def test_index_handles_empty_database(temp_db):
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "Crossings Dashboard" in response.get_data(as_text=True)
