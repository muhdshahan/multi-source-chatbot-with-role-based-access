"""
PDF ingestion module for extracting structured product data and
creating RAG-ready documents from catalogue PDFs.
"""

import pdfplumber
import logging
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chatbot.models import Product

logger = logging.getLogger(__name__)


class PDFIngestor:
    """Handles PDF parsing, data extraction, and document creation."""

    def __init__(self, file_path: str):
        """Initialize with path to PDF file."""
        self.file_path = file_path

    def is_product_page(self, text: str) -> bool:
        """Check if page contains product table."""
        return text and ("Part No" in text and "MRP" in text)

    def parse_products_from_page(self, page):
        """Extract structured product data from tables."""
        products = []
        tables = page.extract_tables()

        if not tables:
            return products

        for table in tables:
            if not table or len(table) < 2:
                continue

            headers = [str(h).strip() if h else "" for h in table[0]]

            # Validate required columns
            if "Part No." not in headers or "MRP" not in headers:
                continue

            try:
                part_idx = headers.index("Part No.")
                desc_idx = headers.index("Description")
                price_idx = headers.index("MRP")
            except ValueError:
                continue

            # Extract category using simple heuristic
            category = "Unknown"
            try:
                text = page.extract_text()
                lines = text.split("\n")

                for line in lines:
                    if any(x in line for x in ["Bit", "Cutter", "Groove", "Flute"]):
                        category = line.strip()
                        break
            except:
                pass

            for row in table[1:]:
                try:
                    part_no = row[part_idx]
                    description = row[desc_idx]
                    price = row[price_idx]

                    if not part_no:
                        continue

                    # Clean price
                    price = str(price).replace(",", "").strip()
                    price = float(price) if price else None

                    products.append({
                        "part_no": part_no.strip(),
                        "description": description.strip() if description else "",
                        "price": price,
                        "category": category,
                        "raw": {
                            "row": row,
                            "category": category
                        }
                    })

                except Exception as e:
                    logger.warning(f"Row parsing failed: {row} | {e}")
                    continue

        logger.info(f"Extracted {len(products)} structured products")
        return products

    def store_products(self, products):
        """Store extracted products in database."""
        objs = []

        for p in products:
            objs.append(
                Product(
                    part_no=p["part_no"],
                    description=p["description"],
                    price=p["price"],
                    raw_data=p["raw"],
                    source="source_1"
                )
            )

        Product.objects.bulk_create(objs, ignore_conflicts=True)
        logger.info(f"Stored {len(objs)} products in DB")

    def create_documents(self):
        """Convert PDF content into RAG-ready documents."""
        all_products = []
        documents = []

        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:

                text = page.extract_text()
                if not self.is_product_page(text):
                    continue

                products = self.parse_products_from_page(page)
                all_products.extend(products)

                for p in products:
                    content = (
                        f"Category: {p['category']}\n"
                        f"Part No: {p['part_no']}\n"
                        f"Description: {p['description']}\n"
                        f"Price: {p['price']}"
                    )

                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "source": "source_1",
                                "type": "product",
                                "part_no": p["part_no"],
                                "category": p["category"]
                            }
                        )
                    )

        self.store_products(all_products)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )

        return splitter.split_documents(documents)