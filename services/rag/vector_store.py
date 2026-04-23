"""
Vector store service for managing FAISS index and embeddings.
Handles creation, loading, and incremental updates of vector database.
"""

import logging

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for FAISS vector store operations."""

    def __init__(self, persist_path="vectorstore/faiss_index"):
        """Initialize embedding model and storage path."""
        self.persist_path = persist_path
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def create_vector_store(self, documents):
        """Create and persist a new FAISS index."""
        logger.info("Creating FAISS vector store...")
        db = FAISS.from_documents(documents, self.embedding_model)
        db.save_local(self.persist_path)
        return db

    def load_vector_store(self):
        """Load existing FAISS index from disk."""
        logger.info("Loading FAISS vector store...")
        return FAISS.load_local(
            self.persist_path,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )
    
    def add_documents(self, documents):
        """Add documents to existing index or create new one."""
        try:
            db = self.load_vector_store()
            db.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to existing index")
        except Exception as e:
            logger.warning(f"Vector store not found or failed to load: {e}")
            db = FAISS.from_documents(documents, self.embedding_model)
            logger.info(f"Created new vector store with {len(documents)} documents")
            
        db.save_local(self.persist_path)