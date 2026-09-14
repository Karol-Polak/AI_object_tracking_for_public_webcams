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


def test_crossing_the_line_invokes_injected_callback_exactly_once():
    calls = []
    counter = LineCounter(frame_width=100, frame_height=100, on_crossing=lambda *args: calls.append(args))

    # Object starts left of the line (config's default line sits at x=85 of a 100px frame)...
    counter.update(_detections_at(x_min=60, x_max=80))
    assert calls == []

    # ...and crosses to the right of it.
    counter.update(_detections_at(x_min=90, x_max=110))
    assert len(calls) == 1


def test_crossing_callback_receives_camera_class_and_direction():
    calls = []
    counter = LineCounter(
        frame_width=100, frame_height=100, camera_id="cam-7",
        on_crossing=lambda *args: calls.append(args),
    )

    counter.update(_detections_at(x_min=60, x_max=80, class_name="car"))
    counter.update(_detections_at(x_min=90, x_max=110, class_name="car"))

    camera_id, object_class, direction = calls[0]
    assert camera_id == "cam-7"
    assert object_class == "car"
    assert direction in ("in", "out")


def test_no_further_movement_does_not_double_count():
    calls = []
    counter = LineCounter(frame_width=100, frame_height=100, on_crossing=lambda *args: calls.append(args))

    counter.update(_detections_at(x_min=60, x_max=80))
    counter.update(_detections_at(x_min=90, x_max=110))
    assert len(calls) == 1

    # Same object, same side of the line, no new crossing.
    counter.update(_detections_at(x_min=92, x_max=112))
    assert len(calls) == 1


def test_no_callback_means_no_persistence_and_no_crash():
    """LineCounter must work standalone, with zero dependency on the storage layer."""
    counter = LineCounter(frame_width=100, frame_height=100)

    counter.update(_detections_at(x_min=60, x_max=80))
    counter.update(_detections_at(x_min=90, x_max=110))  # crosses; must not raise

    assert counter.in_count + counter.out_count == 1
