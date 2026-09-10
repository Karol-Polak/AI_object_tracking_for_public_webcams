"""
Isolated test: run YOLO detection on saved test frames.
"""

import cv2
from ultralytics import YOLO
from pathlib import Path

# Script lives at webcam-tracker/src/detection/test_detect.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # -> webcam-tracker/

FRAMES_DIR = PROJECT_ROOT / "src" / "ingestion" / "data" / "frames"
OUTPUT_DIR = PROJECT_ROOT / "data" / "detections"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

model = YOLO("yolov8n.pt")

for frame_path in sorted(FRAMES_DIR.glob("*.jpg")):
    results = model(frame_path)
    annotated = results[0].plot()

    out_path = OUTPUT_DIR / frame_path.name
    cv2.imwrite(str(out_path), annotated)
    print(f"Detected {len(results[0].boxes)} objects in {frame_path.name} -> saved to {out_path}")