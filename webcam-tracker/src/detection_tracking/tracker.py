"""
Wraps YOLO detection + tracking (.track()) into a reusable class.
Returns supervision Detections, already filtered to relevant classes.
"""

import supervision as sv
from ultralytics import YOLO
from src import config


class Tracker:
    def __init__(self, weights: str = config.MODEL_WEIGHTS, relevant_classes: set = None):
        self.model = YOLO(weights)
        self.relevant_classes = relevant_classes or config.RELEVANT_CLASSES

    def track(self, frame) -> sv.Detections:
        """Run detection+tracking on a single frame, filtered to relevant classes."""
        results = self.model.track(frame, persist=True, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)

        if detections.class_id is not None and len(detections) > 0:
            mask = [results.names[c] in self.relevant_classes for c in detections.class_id]
            detections = detections[mask]

        return detections