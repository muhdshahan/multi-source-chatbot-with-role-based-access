import logging
from services.rag.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RetrieverService:
    def __init__(self):
        self.vector_service = VectorStoreService()
        self.db = self.vector_service.load_vector_store()

    def retrieve(self, query, allowed_sources):
        logger.info(f"Retrieving for query: {query}")
        logger.info(f"Allowed sources: {allowed_sources}")

        # Step 1: Get top results (no filtering)
        docs = self.db.similarity_search(query, k=10)

        # Step 2: Apply access control filter
        filtered_docs = [
            d for d in docs
            if d.metadata.get("source") in allowed_sources
            or d.metadata.get("source_name") in allowed_sources
        ]

        logger.info(f"Retrieved {len(filtered_docs)} filtered documents")
        logger.info(f"After filter: {len(filtered_docs)} documents")
        logger.info(f"Actual sources in results: {[d.metadata.get('source_name') or d.metadata.get('source') for d in filtered_docs]}")

        # Step 3: Return top relevant
        return filtered_docs[:5]