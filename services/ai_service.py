
from groq import Groq
import json
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_ticket(subject, description):

    prompt = f"""
You are an expert support ticket classifier.

Classify the ticket into:
- Queue: IT, HR, or Facilities
- Priority: High, Medium, Low
- Summary: One short sentence

Strict Rules:
- HR → salary, leave, payroll, employee issues
- IT → login, system, software, bugs
- Facilities → AC, electricity, infrastructure

Ticket:
Subject: {subject}
Description: {description}

Return ONLY valid JSON:
{{
  "queue": "",
  "priority": "",
  "summary": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result = response.choices[0].message.content

        print("RAW AI:", result)  
        result = result.replace("```json", "").replace("```", "").strip()

        return json.loads(result)

    except Exception as e:
        print("AI ERROR:", e)

        # fallback
        return {
            "queue": "IT",
            "priority": "Medium",
            "summary": "AI failed to analyze"
        }
    
