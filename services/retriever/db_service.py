from chatbot.models import Product
import logging

logger = logging.getLogger(__name__)

class ProductService:

    def get_price(self, query, allowed_sources):
        products = Product.objects.filter(source__in=allowed_sources)

        for p in products:
            if p.part_no and p.part_no.lower() in query.lower():
                return p
            
        return None
    
    def search_products(self, query, allowed_sources):
        return Product.objects.filter(
            source__in=allowed_sources,
            description_icontains=query
        )[:5]