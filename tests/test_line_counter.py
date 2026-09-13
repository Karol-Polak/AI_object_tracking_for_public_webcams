import numpy as np
import supervision as sv

from src.counting.line_counter import LineCounter


def _detections_at(x_min, x_max, y_min=10, y_max=30, tracker_id=1, class_id=2, class_name="car"):
    return sv.Detections(
        xyxy=np.array([[x_min, y_min, x_max, y_max]], dtype=float),
        class_id=np.array([class_id]),
        tracker_id=np.array([tracker_id]),
        confidence=np.array([0.9]),
        data={"class_name": np.array([class_name])},
    )


def test_crossing_the_line_persists_exactly_one_event(monkeypatch):
    save_crossing_mock_calls = []
    monkeypatch.setattr(
        "src.counting.line_counter.save_crossing",
        lambda camera_id, object_class, direction: save_crossing_mock_calls.append(
            (camera_id, object_class, direction)
        ),
    )

    # Config's default line sits at x=85 (85% of a 100px-wide frame), spanning y=0..40.
    counter = LineCounter(frame_width=100, frame_height=100)

    # Object starts left of the line...
    counter.update(_detections_at(x_min=60, x_max=80))
    assert save_crossing_mock_calls == []

    # ...and crosses to the right of it.
    counter.update(_detections_at(x_min=90, x_max=110))
    assert len(save_crossing_mock_calls) == 1
    camera_id, object_class, direction = save_crossing_mock_calls[0]
    assert camera_id == "default"
    assert object_class == "car"
    assert direction in ("in", "out")


def test_no_further_movement_does_not_double_count(monkeypatch):
    save_crossing_mock_calls = []
    monkeypatch.setattr(
        "src.counting.line_counter.save_crossing",
        lambda camera_id, object_class, direction: save_crossing_mock_calls.append(
            (camera_id, object_class, direction)
        ),
    )

    counter = LineCounter(frame_width=100, frame_height=100)

    counter.update(_detections_at(x_min=60, x_max=80))
    counter.update(_detections_at(x_min=90, x_max=110))
    assert len(save_crossing_mock_calls) == 1

    # Same object, same side of the line, no new crossing.
    counter.update(_detections_at(x_min=92, x_max=112))
    assert len(save_crossing_mock_calls) == 1
