"""
Retriever service for semantic search over vector database.
Applies access control filtering on retrieved documents.
"""

import logging
from services.rag.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RetrieverService:
    """Handles retrieval of relevant documents using FAISS."""

    def __init__(self):
        """Initialize vector store."""
        self.vector_service = VectorStoreService()
        self.db = self.vector_service.load_vector_store()

    def retrieve(self, query, allowed_sources):
        """Retrieve and filter documents based on user access."""
        logger.info(f"Retrieving for query: {query}")
        logger.info(f"Allowed sources: {allowed_sources}")

        docs = self.db.similarity_search(query, k=10)

        filtered_docs = [
            d for d in docs
            if d.metadata.get("source") in allowed_sources
            or d.metadata.get("source_name") in allowed_sources
        ]

        logger.info(f"Documents after filtering: {len(filtered_docs)}")
        logger.debug(
            f"Sources in results: {[d.metadata.get('source_name') or d.metadata.get('source') for d in filtered_docs]}"
        )
        
        return filtered_docs[:5]