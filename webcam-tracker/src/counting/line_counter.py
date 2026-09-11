"""
Wraps supervision's LineZone to count objects crossing a defined line.
Line coordinates are computed from frame size + config fractions.
"""

import supervision as sv
from src import config


class LineCounter:
    def __init__(self, frame_width: int, frame_height: int):
        start_x, start_y = config.LINE_START_FRACTION
        end_x, end_y = config.LINE_END_FRACTION

        line_start = sv.Point(int(frame_width * start_x), int(frame_height * start_y))
        line_end = sv.Point(int(frame_width * end_x), int(frame_height * end_y))

        self.zone = sv.LineZone(start=line_start, end=line_end)
        self.line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5)
        self.box_annotator = sv.BoxAnnotator(thickness=2)
        self.label_annotator = sv.LabelAnnotator()

    def update(self, detections) -> None:
        """Feed detections in; updates internal in/out counts."""
        self.zone.trigger(detections)

    @property
    def in_count(self) -> int:
        return self.zone.in_count

    @property
    def out_count(self) -> int:
        return self.zone.out_count

    def annotate(self, frame, detections):
        """Return an annotated copy of frame with boxes, labels, and the line/count overlay."""
        annotated = self.box_annotator.annotate(scene=frame.copy(), detections=detections)
        annotated = self.label_annotator.annotate(scene=annotated, detections=detections)
        annotated = self.line_annotator.annotate(frame=annotated, line_counter=self.zone)
        return annotated