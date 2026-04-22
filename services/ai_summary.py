
from groq import Groq
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(text):
    try:
        # Handle empty OCR output
        if not text or text.strip() == "":
            return "No readable content found in attachment"
        prompt = f"""
        Summarize the following content clearly in 2 lines:

        {text[:2000]}
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "Unable to generate summary"
    

def generate_ticket_summary(subject, description):
    try:
        text = f"""
        Subject: {subject}
        Description: {description}
        """

        prompt = f"""
Summarize this support issue clearly in 2–3 lines:

{text}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an IT support assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("SUMMARY ERROR:", e)
        return "Summary not available"