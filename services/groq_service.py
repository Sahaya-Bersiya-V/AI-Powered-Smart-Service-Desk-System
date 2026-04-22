from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, context):
    try:
        prompt = f"""
You are a professional helpdesk assistant.

Answer clearly and completely using ONLY the context.

If answer is not found, reply exactly: CONTACT_AGENT

Context:
{context}

Question:
{query}

Give a clear and complete answer.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "Error generating answer"