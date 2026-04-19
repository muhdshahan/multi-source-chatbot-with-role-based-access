import logging
from services.rag.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


class RetrieverService:
    def __init__(self):
        self.vector_service = VectorStoreService()
        self.db = self.vector_service.load_vector_store()

    def retrieve(self, query, allowed_sources):
        logger.info(f"Retrieving for query: {query}")

        results = self.db.similarity_search(
            query, 
            k=5,
            filter={"source": {"$in": allowed_sources}}
        )
        
        docs = self.db.similarity_search(query, k=10)

        # manual filtering
        filtered_docs = [
            d for d in docs
            if d.metadata.get("source") in allowed_sources
        ]

        return filtered_docs[:5]

        return results