import json
import logging

logger = logging.getLogger(__name__)

class VideoSearchService:
    def __init__(self, index_path="data/video_index.json"):
        with open(index_path, "r") as f:
            self.data = json.load(f)

    def parse_query(self, query):
        query = query.lower()

        target_objects = []
        target_color = None

        # normalize words
        if any(x in query for x in ["person", "man", "woman", "lady"]):
            target_objects.append("person")

        if "car" in query or "cars" in query:
            target_objects.append("car")

        if "bus" in query:
            target_objects.append("bus")

        if "bicycle" in query or "bike" in query:
            target_objects.append("bicycle")

        if "bag" in query or "backpack" in query:
            target_objects.append("backpack")

        if "handbag" in query:
            target_objects.append("handbag")

        # color
        if "red" in query:
            target_color = "red"
        elif "white" in query:
            target_color = "white"
        elif "blue" in query:
            target_color = "blue"

        return target_objects, target_color

    def search(self, query, allowed_sources):
        target_objects, target_color = self.parse_query(query)

        results = []

        for frame in self.data:
            matched_boxes = []

            if frame.get("source") not in allowed_sources:
                continue

            for obj in frame["objects"]:
                label = obj["label"]
                color = obj["color"]

                if target_objects and label not in target_objects:
                    continue

                if target_color and color != target_color:
                    continue

                matched_boxes.append(obj)

            if matched_boxes:
                results.append({
                    "frame_id": frame["frame_id"],
                    "timestamp": frame["timestamp"],
                    "frame_path": frame["frame_path"],
                    "matches": matched_boxes
                })

        logger.info(f"Video search query: {query}")
        logger.info(f"Parsed objects: {target_objects}, color: {target_color}")
        logger.info(f"Frames matched: {len(results)}")

        return results[:5]