import pdfplumber
import logging
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chatbot.models import Product

logger = logging.getLogger(__name__)


class PDFIngestor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    # STEP 1: Identify product page
    def is_product_page(self, text: str) -> bool:
        return text and ("Part No" in text and "MRP" in text)

    # STEP 2: Extract structured data from TABLES
    def parse_products_from_page(self, page):
        products = []

        tables = page.extract_tables()

        if not tables:
            return products

        for table in tables:
            if not table or len(table) < 2:
                continue

            headers = [str(h).strip() if h else "" for h in table[0]]

            # Validate table
            if "Part No." not in headers or "MRP" not in headers:
                continue

            try:
                part_idx = headers.index("Part No.")
                desc_idx = headers.index("Description")
                price_idx = headers.index("MRP")
            except ValueError:
                continue

            # Try to extract category (best-effort)
            category = "Unknown"

            # Heuristic: check text above table
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

    # STEP 3: Store in DB
    def store_products(self, products):
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

    # STEP 4: Create RAG documents
    def create_documents(self):
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

        # Store DB
        self.store_products(all_products)

        # Chunk for RAG
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )

        return splitter.split_documents(documents)