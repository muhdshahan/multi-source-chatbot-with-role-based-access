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

    # Step 1: Create documents + tables
    documents, tables_data = ingestor.create_documents()

    # Step 2: Store structured data in DB
    products = ingestor.normalize_products(tables_data)
    ingestor.store_products(products)

    # Step 3: Chunk for RAG
    chunks = ingestor.chunk_documents(documents)

    # Step 4: Store in FAISS
    vector_store = VectorStoreService()
    vector_store.create_vector_store(chunks)

    print("Ingestion completed successfully.")


if __name__ == "__main__":
    run()