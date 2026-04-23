"""
Script to run YouTube ingestion and update vector store.

Initializes Django environment, extracts transcripts from videos,
converts them into documents, and stores them in the vector database.
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ingestion.youtube_ingest import YouTubeIngestor
from services.rag.vector_store import VectorStoreService


VIDEO_URLS = [
    "https://www.youtube.com/watch?v=yIYKR4sgzI8&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=1",
    "https://www.youtube.com/watch?v=ARfXDSkQf1Y&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=2",
    "https://www.youtube.com/watch?v=8nm0G-1uJzA&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=3",
    "https://www.youtube.com/watch?v=vN5cNN2-HWE&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=4",
    "https://www.youtube.com/watch?v=BfKanl1aSG0&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=5",
    "https://www.youtube.com/watch?v=xxFYro8QuXA&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=6",
    "https://www.youtube.com/watch?v=9T0wlKdew6I&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=7",
    "https://www.youtube.com/watch?v=JC56jS2gVUE&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=8",
    "https://www.youtube.com/watch?v=C4N3_XJJ-jU&list=PLblh5JKOoLUKxzEP5HA2d-Li7IJkHfXSe&index=9"
]


def run():
    """Run YouTube ingestion and update vector store."""
    ingestor = YouTubeIngestor()
    docs = ingestor.ingest(VIDEO_URLS)

    vector_service = VectorStoreService()
    vector_service.add_documents(docs)

    print("YouTube ingestion completed.")


if __name__ == "__main__":
    run()