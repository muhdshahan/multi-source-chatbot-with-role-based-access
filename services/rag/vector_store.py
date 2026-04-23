import os
import logging

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self, persist_path="vectorstore/faiss_index"):
        self.persist_path = persist_path
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def create_vector_store(self, documents):
        logger.info("Creating FAISS vector store...")
        db = FAISS.from_documents(documents, self.embedding_model)
        db.save_local(self.persist_path)
        return db

    def load_vector_store(self):
        logger.info("Loading FAISS vector store...")
        return FAISS.load_local(
            self.persist_path,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )
    
    def add_documents(self, documents):
        try:
            db = self.load_vector_store()
            db.add_documents(documents)
            db.save_local(self.persist_path)
        except:
            db = FAISS.from_documents(documents, self.embedding_model)
            db.save_local(self.persist_path)