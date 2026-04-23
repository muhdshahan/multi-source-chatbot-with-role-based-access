from groq import Groq
import os
import logging

logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_response(query, context):
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

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    logger.info("LLM response received")
    return completion.choices[0].message.content