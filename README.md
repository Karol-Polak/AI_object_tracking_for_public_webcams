# AI Object Tracking for Public Webcams

A live vehicle/pedestrian counter built on top of a public YouTube livestream. It pulls frames from the stream, detects and tracks objects with YOLOv8 + ByteTrack, counts how many of each class cross a configurable virtual line (and in which direction), and persists every crossing event to a local database.

## How it works

```
YouTube livestream ──▶ StreamSource ──▶ Tracker ──▶ LineCounter ──▶ SQLite
  (yt-dlp + OpenCV)     yields frames   YOLOv8 +      counts line     crossings
                                        ByteTrack      crossings      table
                                                            │
                                                            ▼
                                                  annotated frames
                                                  (data/pipeline_output/)
```

1. **`src/ingestion/stream_source.py`** resolves the YouTube page URL to a direct stream URL (via `yt-dlp`) and opens it with OpenCV, yielding raw frames.
2. **`src/detection_tracking/tracker.py`** runs YOLOv8 detection + tracking (`model.track(persist=True)`) on each frame and filters detections down to the configured relevant classes (cars, trucks, buses, motorcycles, people).
3. **`src/counting/line_counter.py`** feeds the tracked detections into a `supervision.LineZone`, which counts crossings by **track ID** rather than raw per-frame position — this is what prevents the same object from being counted twice as it crosses.
4. **`src/storage/`** persists each new crossing (camera, object class, direction, timestamp) to SQLite via SQLAlchemy.
5. **`src/pipeline.py`** wires all of the above into a `run()` loop, periodically saving an annotated frame (boxes, labels, the counting line, running totals) to `data/pipeline_output/`.

## Testing

```bash
pip install -r requirements.txt
pytest -v
```

Runs automatically on every push via GitHub Actions (`.github/workflows/ci.yml`).

## Dashboard

A small read-only Flask app for viewing aggregate crossing counts collected in the database:

```bash
python -m src.dashboard.app
```

Then open http://127.0.0.1:5000 — shows total in/out counts and a bar chart of crossings by object class and direction, with a manual refresh button. The same data is available as JSON at `/api/summary`.

## Setup

Requires Python 3.12+.

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The YOLOv8n weights (`yolov8n.pt`) are downloaded automatically by Ultralytics on first run if not already present locally.

## Usage

```bash
python -m src.pipeline
```

By default this processes 60 seconds of the configured stream, saving an annotated frame every 15 frames to `data/pipeline_output/` and printing final in/out counts. To run it differently, call `run()` directly:

```python
from src.pipeline import run

run(duration_seconds=120, save_every_n_frames=30, save_output=True)
```

## Configuration

All tunables live in `src/config.py`:

| Setting | Purpose |
|---|---|
| `STREAM_PAGE_URL` | YouTube page for the livestream to pull from |
| `STREAM_FORMAT` | yt-dlp format selector (resolution/codec) |
| `MODEL_WEIGHTS` | YOLO weights file to load |
| `RELEVANT_CLASSES` | Object classes to detect/count |
| `LINE_START_FRACTION` / `LINE_END_FRACTION` | Counting line position, as fractions of frame width/height — so the line adapts automatically to the stream's actual resolution |

The project currently targets a single camera/stream per run. The database schema already carries a `camera_id` per crossing, anticipating multi-camera support later.

## Tech stack

Python · Ultralytics YOLOv8 · supervision (ByteTrack + LineZone) · OpenCV · yt-dlp · SQLAlchemy · SQLite · Flask · Chart.js

## Known limitations

This is an early-stage prototype, not a production service:

- Single camera / single counting line per run (see Configuration above).
- Saved annotated frames (which may contain identifiable people/vehicles from the public feed) are kept indefinitely with no retention policy — something to address before any real deployment.

## License

[MIT](LICENSE)
