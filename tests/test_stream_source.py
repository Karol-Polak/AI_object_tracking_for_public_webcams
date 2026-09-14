import pytest
import yt_dlp

from src.ingestion import stream_source as stream_source_module
from src.ingestion.stream_source import StreamSource


class _FakeCapture:
    """Scripted cv2.VideoCapture-alike: read() pops (ret, frame) tuples in order."""

    def __init__(self, results):
        self._results = list(results)

    def read(self):
        return self._results.pop(0)


class _FailingYDL:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def extract_info(self, url, download):
        raise yt_dlp.utils.DownloadError("simulated resolution failure")


def test_resolve_stream_url_wraps_yt_dlp_errors_with_context(monkeypatch):
    monkeypatch.setattr(stream_source_module.yt_dlp, "YoutubeDL", _FailingYDL)
    source = StreamSource("https://example.com/live")

    with pytest.raises(RuntimeError, match="https://example.com/live"):
        source.open()


def test_frames_retries_transient_read_failures_then_recovers(monkeypatch):
    monkeypatch.setattr(stream_source_module.time, "sleep", lambda seconds: None)

    source = StreamSource("https://example.com/live", max_read_retries=2, retry_delay_seconds=0)
    source.cap = _FakeCapture([
        (True, "frame1"),
        (False, None),
        (True, "frame2"),
        (False, None),
        (False, None),
        (False, None),  # 3rd consecutive failure exceeds max_read_retries=2 -> stop
    ])

    frames = list(source.frames())

    assert frames == ["frame1", "frame2"]


def test_frames_gives_up_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr(stream_source_module.time, "sleep", lambda seconds: None)

    source = StreamSource("https://example.com/live", max_read_retries=1, retry_delay_seconds=0)
    source.cap = _FakeCapture([(False, None), (False, None)])

    frames = list(source.frames())

    assert frames == []
