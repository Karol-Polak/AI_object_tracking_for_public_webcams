"""
Handles resolving a YouTube livestream URL and yielding frames.
Reusable across any camera source that yt-dlp can resolve.
"""

import time

import cv2
import yt_dlp
from src import config


class StreamSource:
    def __init__(
        self,
        page_url: str,
        stream_format: str = config.STREAM_FORMAT,
        max_read_retries: int = 5,
        retry_delay_seconds: float = 1.0,
    ):
        self.page_url = page_url
        self.stream_format = stream_format
        self.max_read_retries = max_read_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.cap = None

    def _resolve_stream_url(self) -> str:
        ydl_opts = {"quiet": True, "format": self.stream_format}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.page_url, download=False)
                return info["url"]
        except yt_dlp.utils.DownloadError as exc:
            raise RuntimeError(f"Could not resolve stream URL for {self.page_url}: {exc}") from exc

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
        """Generator yielding frames. Tolerates transient read failures (common
        on a live stream) by retrying up to max_read_retries times before giving up."""
        consecutive_failures = 0
        while True:
            ret, frame = self.cap.read()
            if ret:
                consecutive_failures = 0
                yield frame
                continue

            consecutive_failures += 1
            if consecutive_failures > self.max_read_retries:
                break
            time.sleep(self.retry_delay_seconds)

    def release(self):
        if self.cap:
            self.cap.release()