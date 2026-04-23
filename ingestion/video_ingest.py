"""
Video ingestion module for extracting frames, detecting objects,
and storing metadata for video-based search.
"""

import cv2
import os
import json
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class VideoIngestor:
    """Handles video processing, object detection, and indexing."""

    def __init__(self, video_path, output_dir="data/frames"):
        """Initialize model, and paths."""
        self.video_path = video_path
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.model = YOLO("yolov8m.pt")

    def extract_frames(self, interval=100):
        """Extract frames at fixed interval with timestamps."""
        cap = cv2.VideoCapture(self.video_path)

        frames = []
        frame_id = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_id % interval == 0:
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                frames.append((frame, timestamp, frame_id))

            frame_id += 1

        cap.release()
        return frames

    def detect_color(self, crop):
        """Detect dominant color from cropped object region."""
        if crop is None or crop.size == 0:
            return "unknown"

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        color_ranges = {
            "red": [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (180, 255, 255))],
            "white": [((0, 0, 200), (180, 40, 255))],
            "blue": [((94, 80, 2), (126, 255, 255))],
            "green": [((35, 50, 50), (85, 255, 255))],
            "black": [((0, 0, 0), (180, 255, 50))]
        }

        detected_color = "unknown"
        max_ratio = 0

        for color, ranges in color_ranges.items():
            mask_total = None

            for lower, upper in ranges:
                mask = cv2.inRange(hsv, lower, upper)
                mask_total = mask if mask_total is None else (mask_total | mask)

            ratio = (mask_total > 0).sum() / mask_total.size

            if ratio > max_ratio and ratio > 0.05:
                max_ratio = ratio
                detected_color = color

        return detected_color

    def detect_objects(self, frames):
        """Run YOLO detection and extract object metadata."""
        results = []

        for frame, timestamp, frame_id in frames:
            detections = self.model(frame)
            logger.info(f"Processing frame {frame_id} at {timestamp}")

            boxes_in_frame = []
            seen_labels = set()

            for det in detections:
                for box in det.boxes:
                    conf = float(box.conf[0])

                    if conf < 0.5:
                        continue

                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]

                    # Avoid duplicate labels per frame
                    if label in seen_labels:
                        continue
                    seen_labels.add(label)

                    # Bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    crop = frame[y1:y2, x1:x2]
                    color = self.detect_color(crop)

                    boxes_in_frame.append({
                        "label": label,
                        "color": color,
                        "bbox": [x1, y1, x2, y2]
                    })

            # Save RAW frame
            frame_path = os.path.join(self.output_dir, f"{frame_id}.jpg")
            cv2.imwrite(frame_path, frame)

            results.append({
                "frame_id": frame_id,
                "timestamp": round(timestamp, 2),
                "objects": boxes_in_frame,
                "frame_path": frame_path,
                "scene_tags": [],
                "source": "source_3"
            })

        return results

    def ingest(self):
        """Run full pipeline: extract frames, detect objects, store index."""
        frames = self.extract_frames(interval=100)
        detections = self.detect_objects(frames)

        with open("data/video_index.json", "w") as f:
            json.dump(detections, f, indent=2)

        logger.info(f"Stored {len(detections)} detections")
        return detections