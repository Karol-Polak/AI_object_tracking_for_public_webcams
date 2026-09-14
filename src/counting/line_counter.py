"""
Wraps supervision's LineZone to count objects crossing a defined line.
Reports each individual crossing event via an injected callback, so this
class has no dependency on how (or whether) crossings get persisted.
"""

from typing import Callable, Optional

import supervision as sv
from src import config


class LineCounter:
    def __init__(
        self,
        frame_width: int,
        frame_height: int,
        camera_id: str = "default",
        on_crossing: Optional[Callable[[str, str, str], None]] = None,
    ):
        start_x, start_y = config.LINE_START_FRACTION
        end_x, end_y = config.LINE_END_FRACTION

        line_start = sv.Point(int(frame_width * start_x), int(frame_height * start_y))
        line_end = sv.Point(int(frame_width * end_x), int(frame_height * end_y))

        self.zone = sv.LineZone(start=line_start, end=line_end)
        self.line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        self.box_annotator = sv.BoxAnnotator(thickness=2)
        self.label_annotator = sv.LabelAnnotator()

        self.camera_id = camera_id
        self._on_crossing = on_crossing
        self._prev_in_per_class = {}
        self._prev_out_per_class = {}

    def update(self, detections) -> None:
        """Feed detections in; updates counts and persists any new crossings."""
        self.zone.trigger(detections)
        self._persist_deltas(detections)

    def _persist_deltas(self, detections):
        current_in = dict(self.zone.in_count_per_class)
        current_out = dict(self.zone.out_count_per_class)

        if self._on_crossing is not None:
            # figure out class_id -> name mapping from current detections batch
            id_to_name = {}
            if detections.class_id is not None and detections.data.get("class_name") is not None:
                for cid, cname in zip(detections.class_id, detections.data["class_name"]):
                    id_to_name[cid] = cname

            for direction, current, previous in (
                ("in", current_in, self._prev_in_per_class),
                ("out", current_out, self._prev_out_per_class),
            ):
                for class_id, count in current.items():
                    prev = previous.get(class_id, 0)
                    if count > prev:
                        class_name = id_to_name.get(class_id, str(class_id))
                        for _ in range(count - prev):
                            self._on_crossing(self.camera_id, class_name, direction)

        self._prev_in_per_class = current_in
        self._prev_out_per_class = current_out

    @property
    def in_count(self) -> int:
        return self.zone.in_count

    @property
    def out_count(self) -> int:
        return self.zone.out_count

    def annotate(self, frame, detections):
        annotated = self.box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated = self.label_annotator.annotate(scene=annotated, detections=detections)
        annotated = self.line_annotator.annotate(frame=annotated, line_counter=self.zone)
        return annotated