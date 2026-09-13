import numpy as np
import supervision as sv

from src.detection_tracking.tracker import Tracker


class _FakeResults:
    """Stand-in for an ultralytics Results object: track() only ever reads .names."""

    def __init__(self, names):
        self.names = names


def _fake_detections():
    # class_id 0=person, 2=car, 5=bus (arbitrary, mirrors COCO-style ids)
    return sv.Detections(
        xyxy=np.array([[0, 0, 10, 10], [0, 0, 10, 10], [0, 0, 10, 10]], dtype=float),
        class_id=np.array([0, 2, 5]),
        confidence=np.array([0.9, 0.8, 0.7]),
    )


def test_track_filters_out_irrelevant_classes(monkeypatch):
    names = {0: "person", 2: "car", 5: "bus"}
    monkeypatch.setattr(
        "src.detection_tracking.tracker.YOLO",
        lambda weights: type("FakeModel", (), {
            "track": lambda self, frame, persist, verbose: [_FakeResults(names)],
        })(),
    )
    monkeypatch.setattr(sv.Detections, "from_ultralytics", lambda results: _fake_detections())

    tracker = Tracker(weights="unused.pt", relevant_classes={"car", "bus"})
    result = tracker.track(frame=None)

    assert len(result) == 2
    assert set(result.class_id) == {2, 5}


def test_track_keeps_all_relevant_classes(monkeypatch):
    names = {0: "person", 2: "car", 5: "bus"}
    monkeypatch.setattr(
        "src.detection_tracking.tracker.YOLO",
        lambda weights: type("FakeModel", (), {
            "track": lambda self, frame, persist, verbose: [_FakeResults(names)],
        })(),
    )
    monkeypatch.setattr(sv.Detections, "from_ultralytics", lambda results: _fake_detections())

    tracker = Tracker(weights="unused.pt", relevant_classes={"person", "car", "bus"})
    result = tracker.track(frame=None)

    assert len(result) == 3
