import logging
import re
import os
import cv2
import uuid
import time

from services.retriever.retriever import RetrieverService
from services.retriever.db_service import ProductService
from services.rag.router import QueryRouter
from services.llm.groq_client import generate_response
from services.video.video_service import VideoSearchService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.retriever = RetrieverService()
        self.product_service = ProductService()
        self.router = QueryRouter()
        self.video_service = VideoSearchService()

    def log_response(self, request_id, response):
        preview = response[:300]
        logger.info(f"[{request_id}] RESPONSE PREVIEW: {preview}")

    def handle_query(self, user, query):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        allowed_sources = user.get_allowed_sources()
        query_lower = query.lower()

        logger.info(f"[{request_id}] USER: {user.username}")
        logger.info(f"[{request_id}] QUERY: {query}")
        logger.info(f"[{request_id}] ALLOWED SOURCES: {allowed_sources}")

        # MULTIPLE PART NUMBERS
        part_numbers = re.findall(r"[A-Z]-\d{5}", query.upper())

        if part_numbers:
            logger.info(f"[{request_id}] MULTI PART SEARCH: {part_numbers}")

            response = "Product Details:<br><br>"

            for idx, part in enumerate(part_numbers, 1):
                product = self.product_service.get_by_part_number(part, allowed_sources)

                if product:
                    logger.info(f"[{request_id}] DB HIT: {part}")
                    response += (
                        f"{idx}. {part}:<br>"
                        f"- Part No: {product.part_no}<br>"
                        f"- Description: {product.description}<br>"
                        f"- Price: ₹{product.price}<br><br>"
                    )
                else:
                    logger.warning(f"[{request_id}] DB MISS: {part}")
                    return "information not available or is restricted<br>"
            
            logger.info(f"[{request_id}] RESPONSE RETURNED (MULTI PART)")
            self.log_response(request_id, response)
            return response

        # PRICE FILTER 
        price_match = re.search(r"(above|greater than|over|higher than|below|less than).*?(\d+)", query_lower)

        if price_match:
            value = float(price_match.group(2))
            condition = price_match.group(1)

            logger.info(f"[{request_id}] PRICE FILTER: {condition} {value}")

            if any(x in condition for x in ["above", "greater", "over", "higher"]):
                products = self.product_service.filter_by_price(value, allowed_sources)
            else:
                products = self.product_service.filter_below_price(value, allowed_sources)

            logger.info(f"[{request_id}] PRODUCTS FOUND: {len(products)}")

            if products:
                response = "Products found:<br><br>"
                for p in products:
                    response += f"{p.part_no} - ₹{p.price} - {p.description}<br>"

                self.log_response(request_id, response)
                return response

        # MULTI PRODUCT SEARCH
        products = self.product_service.search_multiple_products(query, allowed_sources)

        if products:
            logger.info(f"[{request_id}] MULTI PRODUCT MATCH: {len(products)}")

            context = ""
            for p in products:
                context += f"{p.part_no} - ₹{p.price} - {p.description}\n"

            try:
                logger.info(f"[{request_id}] Sending MULTI PRODUCT context to LLM")
                response = generate_response(query, context)
                self.log_response(request_id, response)
                return response
            except Exception as e:
                logger.error(f"[{request_id}] LLM ERROR (MULTI PRODUCT): {str(e)}")
                return "Error generating response."

        # SINGLE PRODUCT SEARCH
        product = self.product_service.search_product(query, allowed_sources)
        
        if product:
            logger.info(f"[{request_id}] SINGLE PRODUCT HIT: {product.part_no}")

            context = f"""
            Product Details:
            Part No: {product.part_no}
            Description: {product.description}
            Price: ₹{product.price}
            """

            try:
                logger.info(f"[{request_id}] Sending SINGLE PRODUCT to LLM")
                response = generate_response(query, context)
                self.log_response(request_id, response)
                return response
            except Exception as e:
                logger.error(f"[{request_id}] LLM ERROR (SINGLE PRODUCT): {str(e)}")
                return "Error generating response."

        # VIDEO SEARCH
        query_type = self.router.classify(query)

        if query_type == "video":
            logger.info(f"[{request_id}] VIDEO QUERY DETECTED")

            results = self.video_service.search(query, allowed_sources)

            logger.info(f"[{request_id}] VIDEO RESULTS: {len(results)}")

            if not results:
                return "information not available or is restricted"

            response = "Matches found:<br><br>"

            for r in results:
                logger.info(f"[{request_id}] Frame {r['frame_id']} @ {r['timestamp']}")

                frame = cv2.imread(r["frame_path"])

                for obj in r["matches"]:
                    x1, y1, x2, y2 = obj["bbox"]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    label = f"{obj['label']} ({obj['color']})"

                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

                filename = f"result_{r['frame_id']}.jpg"
                save_path = os.path.join("data/frames", filename)
                cv2.imwrite(save_path, frame)

                response += (
                    f"- at {r['timestamp']} sec<br>"
                    f"<img src='http://127.0.0.1:8000/media/frames/{filename}' width='300'><br><br>"
                )

            self.log_response(request_id, response)
            return response

        # RAG
        logger.info(f"[{request_id}] RAG TRIGGERED")

        docs = self.retriever.retrieve(query, allowed_sources)

        logger.info(f"[{request_id}] DOCS RETRIEVED: {len(docs)}")

        if not docs:
            return "information not available or is restricted"

        context = ""
        sources = set()

        for i, d in enumerate(docs):
            logger.info(
                f"[{request_id}] DOC {i} | Source: {d.metadata.get('source')} | "
                f"Preview: {d.page_content[:100]}"
            )

            context += d.page_content + "\n\n"
            sources.add(d.metadata.get("source"))

        try:
            logger.info(f"[{request_id}] Sending RAG context to LLM (length={len(context)})")
            response = generate_response(query, context)
        except Exception:
            logger.error(f"[{request_id}] LLM ERROR (RAG): {str(e)}")
            return "Error generating response."

        end_time = time.time()
        logger.info(f"[{request_id}] RESPONSE GENERATED in {round(end_time - start_time, 2)}s")

        self.log_response(request_id, response)
        return f"{response}<br><br>Sources: {', '.join(sources)}"