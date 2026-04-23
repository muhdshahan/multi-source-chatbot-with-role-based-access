"""
Service layer for product retrieval and filtering.
Handles structured queries on product database.
"""

import re
import logging
from chatbot.models import Product

logger = logging.getLogger(__name__)

class ProductService:
    """Provides methods for querying product data."""

    def extract_part_number(self, query):
        """Extract part number from query if present."""
        match = re.search(r"[A-Z]-\d{5}", query.upper())
        return match.group() if match else None

    def search_product(self, query, allowed_sources):
        """Search product by part number within allowed sources."""
        products = Product.objects.filter(source__in=allowed_sources)
        logger.info(f"Searching product for query: {query}")

        part_no = self.extract_part_number(query)
        if part_no:
            product = products.filter(part_no=part_no).first()
            if product:
                return product

        return None
    
    def get_by_part_number(self, part_no, allowed_sources):
        """Retrieve product by exact part number."""
        return Product.objects.filter(
            part_no__iexact=part_no,
            source__in=allowed_sources
        ).first()


    def filter_by_price(self, value, allowed_sources):
        """Return products with price greater than given value."""
        return Product.objects.filter(
            price__gt=value,
            source__in=allowed_sources
        )[:10]


    def filter_below_price(self, value, allowed_sources):
        """Return products with price less than given value."""
        return Product.objects.filter(
            price__lt=value,
            source__in=allowed_sources
        )[:10]


    def search_multiple_products(self, query, allowed_sources):
        """Find multiple relevant products using keyword overlap."""
        products = Product.objects.filter(source__in=allowed_sources)

        query = query.lower()
        query_words = set(re.findall(r'\w+', query))

        results = []

        for p in products:
            text = f"{p.part_no} {p.description}".lower()
            text_words = set(re.findall(r'\w+', text))

            score = len(query_words & text_words)

            if score >= 2:
                results.append((score, p))

        results.sort(reverse=True, key=lambda x: x[0])

        return [p for _, p in results[:5]]