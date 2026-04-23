"""
Script to run video ingestion and generate indexed frame data.

Initializes Django environment, processes video frames,
performs object detection, and stores results for retrieval.
"""

import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ingestion.video_ingest import VideoIngestor

VIDEO_PATH = "data/People-Walking-Free.mp4"


def run():
    """Run video ingestion and store detection results."""
    if not os.path.exists(VIDEO_PATH):
        print(f"Video not found at {VIDEO_PATH}")
        return 
    
    ingestor = VideoIngestor(VIDEO_PATH)
    detections = ingestor.ingest()

    print(f"Video ingestion completed.")
    print(f"Total detections: {len(detections)}")
    print("Saved to: data/video_index.json")


if __name__ == "__main__":
    run()