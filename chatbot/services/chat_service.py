from services. retriever.retriever import RetrieverService
from services.retriever.db_service import ProductService
from services.rag.router import QueryRouter
from services.llm.groq_client import generate_response


class ChatService:
    def __init__(self):
        self.retriever = RetrieverService()
        self.product_service = ProductService()
        self.router = QueryRouter()

    def handle_query(self, user, query):
        allowed_sources = user.get_allowed_sources()
        query_type = self.router.classify(query)

        # DB Logic
        if query_type == "price":
            product = self.product_service.get_price(query, allowed_sources)

            if product:
                return f"Price: {product.price}"
            else:
                return "Product not found"
            
        # RAG Logic
        docs = self.retriever.retrieve(query, allowed_sources)

        context = "\n".join([d.page_content for d in docs])

        return generate_response(query, context)