import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from ingestion.pdf_ingest import PDFIngestor
from services.rag.vector_store import VectorStoreService

PDF_PATH = "data/makita_catalogue.pdf"

def run():
    ingestor = PDFIngestor(PDF_PATH)

    documents = ingestor.create_documents()

    vector_service = VectorStoreService()
    vector_service.create_vector_store(documents)

    print("Ingestion completed successfully")


if __name__ == "__main__":
    run()