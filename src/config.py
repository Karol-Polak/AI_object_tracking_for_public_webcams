"""
Central configuration for the webcam tracker.
Keep camera-specific and tunable values here instead of scattered across modules.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Camera source ---
STREAM_PAGE_URL = "https://www.youtube.com/watch?v=1EiC9bvVGnk"
STREAM_FORMAT = "bestvideo[ext=mp4][height<=720]"

# --- Detection ---
MODEL_WEIGHTS = "yolov8n.pt"
RELEVANT_CLASSES = {"car", "truck", "bus", "person", "motorcycle"}

# --- Counting line (as fractions of frame width/height, tuned for this camera) ---
LINE_START_FRACTION = (0.85, 0.0)
LINE_END_FRACTION = (0.85, 0.4)

# --- Output ---
DATA_DIR = PROJECT_ROOT / "data"