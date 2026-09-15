"""
Flask dashboard: serves aggregate crossing-count data collected by the
pipeline. Read-only — never writes to the database.
"""

from flask import Flask, jsonify, render_template

from src.storage.db import get_crossing_summary, init_db


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        summary = get_crossing_summary()
        total_in = sum(counts.get("in", 0) for counts in summary.values())
        total_out = sum(counts.get("out", 0) for counts in summary.values())
        return render_template("index.html", summary=summary, total_in=total_in, total_out=total_out)

    @app.get("/api/summary")
    def api_summary():
        return jsonify(get_crossing_summary())

    return app


if __name__ == "__main__":
    init_db()
    create_app().run(debug=True)
