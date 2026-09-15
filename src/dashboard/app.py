"""
Flask dashboard: serves aggregate crossing-count data collected by the
pipeline. Read-only — never writes to the database.
"""

from flask import Flask, jsonify

from src.storage.db import get_crossing_summary, init_db


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/api/summary")
    def api_summary():
        return jsonify(get_crossing_summary())

    return app


if __name__ == "__main__":
    init_db()
    create_app().run(debug=True)
