"""
Handles resolving a YouTube livestream URL and yielding frames.
Reusable across any camera source that yt-dlp can resolve.
"""

import cv2
import yt_dlp
from src import config


class StreamSource:
    def __init__(self, page_url: str, stream_format: str = config.STREAM_FORMAT):
        self.page_url = page_url
        self.stream_format = stream_format
        self.cap = None

    def _resolve_stream_url(self) -> str:
        ydl_opts = {"quiet": True, "format": self.stream_format}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.page_url, download=False)
            return info["url"]

    def open(self):
        stream_url = self._resolve_stream_url()
        self.cap = cv2.VideoCapture(stream_url)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open stream: {self.page_url}")
        return self

    @property
    def fps(self) -> float:
        return self.cap.get(cv2.CAP_PROP_FPS) or 30

    @property
    def frame_size(self) -> tuple[int, int]:
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return w, h

    def frames(self):
        """Generator yielding frames until the stream ends or fails."""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame

    def release(self):
        if self.cap:
            self.cap.release()