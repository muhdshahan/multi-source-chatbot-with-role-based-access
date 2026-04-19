from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_response(query, context):
    prompt= f"""
    Answer strictly based on the context below.
    If not found, say "information not available".

    Context:
    {context}

    Question:
    {query}
    """

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content