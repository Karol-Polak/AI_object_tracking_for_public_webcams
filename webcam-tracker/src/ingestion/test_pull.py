"""
Isolated test: test if it's possible to pull live frames from youtube livestream.
"""

import cv2
import yt_dlp
from pathlib import Path

#TOWN STREAM - JACKSONE TOWN
STREAM_PAGE_URL = "https://www.youtube.com/watch?v=1EiC9bvVGnk"

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # webcam-tracker/
OUTPUT_DIR = PROJECT_ROOT / "data" / "frames"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_stream_url(youtube_url: str) -> str:
    ydl_opts = {
        "quiet": True,
        "format": "bestvideo[ext=mp4][height<=720]",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info["url"]

def pull_test_frames(stream_url: str, num_frames: int = 5, every_n_seconds: int = 2):
    """Pull a handful of frames and save them to disk to visually confirm the feed."""
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        raise RuntimeError("Could not open stream. Check the URL or your connection.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25  # fallback if fps isn't reported
    frame_interval = int(fps * every_n_seconds)

    saved = 0
    frame_count = 0

    while saved < num_frames:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame — stream may have dropped.")
            break

        if frame_count % frame_interval == 0:
            out_path = OUTPUT_DIR / f"frame_{saved:03d}.jpg"
            cv2.imwrite(str(out_path), frame)
            print(f"Saved {out_path}")
            saved += 1

        frame_count += 1

    cap.release()


if __name__ == "__main__":
    print("Resolving stream URL...")
    url = get_stream_url(STREAM_PAGE_URL)
    print(f"Resolved stream URL (truncated): {url[:80]}...")

    print("Pulling test frames...")
    pull_test_frames(url, num_frames=5, every_n_seconds=2)

    print("Done. Check data/frames/ for output.")