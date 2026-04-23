import logging
import time
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class YouTubeIngestor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,         
            chunk_overlap=130
        )

    def extract_video_id(self, url):
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        return None
        
    def extract_video_index(self, url):
        if "index=" in url:
            return url.split("index=")[1].split("&")[0]
        return "unknown"

    def get_transcript(self, video_id):
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id=video_id)

            return [
                {"text": t.text, "start": t.start}
                for t in transcript
            ]

        except Exception as e:
            logger.error(f"Transcript fetch failed: {e}")
            return []

    def build_full_text(self, transcript):
        full_text = ""
        timestamps = []

        for t in transcript:
            full_text += t["text"] + " "
            timestamps.append(t["start"])

        return full_text.strip(), timestamps

    # create chunks from full text
    def create_documents(self, full_text, timestamps, video_id, video_index, source_name):
        docs = []

        chunks = self.splitter.split_text(full_text)

        for i, chunk in enumerate(chunks):
            timestamp = timestamps[min(i, len(timestamps) - 1)]

            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "source_2",
                        "source_name": source_name,
                        "video_id": video_id,
                        "video_index": video_index,
                        "timestamp": timestamp
                    }
                )
            )

        return docs

    def ingest(self, video_urls):
        all_docs = []

        for url in video_urls:
            video_id = self.extract_video_id(url)
            video_index = self.extract_video_index(url)
            source_name = f"source_2_video_{video_index}"

            if not video_id:
                continue

            transcript = self.get_transcript(video_id)

            if not transcript:
                continue

            full_text, timestamps = self.build_full_text(transcript)

            docs = self.create_documents(
                full_text,
                timestamps,
                video_id,
                video_index,
                source_name
            )

            all_docs.extend(docs)

            logger.info(f"Ingested video: {video_id} with {len(docs)} chunks")

            time.sleep(5)

        return all_docs