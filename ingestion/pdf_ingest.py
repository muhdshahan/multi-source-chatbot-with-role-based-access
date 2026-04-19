import os
import tempfile
import pdfplumber
import camelot
import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from chatbot.models import Product

os.makedirs("C:/temp", exist_ok=True)
os.environ["TMPDIR"] = "C:/temp"
tempfile.tempdir = "C:/temp"

logger = logging.getLogger(__name__)


class PDFIngestor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self):
        logger.info("Extracting text form PDF...")
        text_data = []

        with pdfplumber.open(self.file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_data.append({
                        "content": text,
                        "page": i + 1
                    })

        return text_data
    
    def _make_columns_unique(self, columns):
        seen = {}
        new_cols = []

        for col in columns:
            if col in seen:
                seen[col] += 1
                new_cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                new_cols.append(col)

        return new_cols

    def extract_tables(self):
        logger.info("Extracting tables using Camelot...")
        tables_data = []

        try:
            tables = camelot.read_pdf(self.file_path, pages='all')

            for i, table in enumerate(tables):
                df = table.df

                # Fix header
                df.columns = df.iloc[0]
                df = df[1:]
                df = df.reset_index(drop=True)

                # FIX duplicate columns
                df.columns = self._make_columns_unique(df.columns)

                # Convert table to structured dict
                tables_data.append({
                    "data": df.to_dict(orient="records"),
                    "columns": list(df.columns),
                    "table_id": i
                })

            del tables

        except Exception as e:
            logger.error(f"Table extraction failed: {str(e)}", exc_info=True)

        finally:
            import gc
            gc.collect() 
    
        return tables_data
    
    def normalize_products(self, tables_data):
        logger.info("Normalizing products from tables...")

        products = []

        for table in tables_data:
            for row in table["data"]:
                product={
                    "part_no": row.get("Part No") or row.get("Part No."),
                    "description": row.get("Description"),
                    "price": self._extract_price(row),
                    "raw": row
                }
                products.append(product)
            
        return products

    def _extract_price(self, row):
        for key, value in row.items():
                if isinstance(key, str):
                    if "MRP" in key or "Price" in key:
                        return self._clean_price(value)

                # fallback: detect numeric price
                if isinstance(value, (int, float)):
                    return value

                if isinstance(value, str) and value.replace(",", "").isdigit():
                    return int(value.replace(",", ""))

        return None
    
    def store_products(self, products):
        logger.info("Storing products in database...")

        count = 0
        for p in products:
            try:
                Product.objects.create(
                    part_no=p["part_no"],
                    description=p["description"],
                    price=p["price"],
                    raw_data=p["raw"],
                    source="source_1"
                )
                count += 1
            except Exception as e:
                logger.error(f"Failed to store product:{e}")

        logger.info(f"Stored {count} products")

    def create_documents(self):
        logger.info("Creating documents for RAG...")

        text_data = self.extract_text()
        tables_data = self.extract_tables()

        documents = []

        for item in text_data:
            documents.append(
                Document(
                    page_content=item["content"],
                    metadata={
                        "source": "source_1",
                        "type": "text",
                        "page": item["page"]
                    }
                )
            )

        for table in tables_data:
            for row in table["data"]:
                row_str = " | ".join([f"{k}: {v}" for k, v in row.items()])

                documents.append(
                    Document(
                        page_content=row_str,
                        metadata={
                            "source": "source_1",
                            "type": "table",
                            "table_id": table["table_id"]
                        }
                    )
                )
            
        return documents, tables_data
        
    def chunk_documents(self, documents):
        logger.info("Chunking documents...")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )

        return splitter.split_documents(documents)