"""
LLM client module for generating grounded responses using Groq API.
Ensures responses are based strictly on provided context.
"""

import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY not set in environment variables")

client = Groq(api_key=API_KEY)


def generate_response(query, context):
    """Generate response using LLM with strict context grounding."""

    prompt= f"""
    Answer strictly based on the context below.
    If not found, say "information not available or is restricted".

    Context:
    {context}

    Question:
    {query}
    """

    logger.info("Sending request to LLM")
    logger.info(f"Prompt length: {len(prompt)}")

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        response = completion.choices[0].message.content.strip()

        logger.info("LLM response received")
        return response

    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        return "Error generating response."