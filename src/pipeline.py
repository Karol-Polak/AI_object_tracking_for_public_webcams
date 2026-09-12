"""
Main pipeline: connects ingestion -> tracking -> counting.
Run this to process the live stream continuously.
"""

import cv2
from src import config
from src.ingestion.stream_source import StreamSource
from src.detection_tracking.tracker import Tracker
from src.counting.line_counter import LineCounter
from src.storage.db import init_db


init_db()

def run(duration_seconds: int = 60, save_every_n_frames: int = 15, save_output: bool = True):
    output_dir = config.DATA_DIR / "pipeline_output"
    if save_output:
        output_dir.mkdir(parents=True, exist_ok=True)

    print("Opening stream...")
    source = StreamSource(config.STREAM_PAGE_URL).open()
    width, height = source.frame_size
    max_frames = int(source.fps * duration_seconds)

    tracker = Tracker()
    counter = LineCounter(width, height)

    frame_count = 0
    saved_count = 0

    try:
        for frame in source.frames():
            if frame_count >= max_frames:
                break

            detections = tracker.track(frame)
            counter.update(detections)

            if save_output and frame_count % save_every_n_frames == 0:
                annotated = counter.annotate(frame, detections)
                out_path = output_dir / f"frame_{saved_count:03d}.jpg"
                cv2.imwrite(str(out_path), annotated)
                print(f"[{frame_count}] Saved {out_path.name} | in={counter.in_count} out={counter.out_count}")
                saved_count += 1

            frame_count += 1
    finally:
        source.release()

    print(f"\nFinal counts — in: {counter.in_count}, out: {counter.out_count}")


if __name__ == "__main__":
    run(duration_seconds=60, save_every_n_frames=15)