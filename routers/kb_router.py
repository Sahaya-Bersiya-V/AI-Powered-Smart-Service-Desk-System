
from fastapi import APIRouter, UploadFile, File
import shutil
import os
from services.rag_service import remove_file_from_kb
from services.rag_service import add_pdf_to_kb, search
from services.groq_service import generate_answer
from services.faq_service import search_faq
router = APIRouter(prefix="/kb", tags=["Knowledge Base"])

KB_FOLDER = "kb_files"


# CREATE FOLDER IF NOT EXISTS
os.makedirs(KB_FOLDER, exist_ok=True)
def handle_small_talk(query):
    q = query.lower()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    thanks = ["thank you", "thanks", "thx"]

    if any(greet in q for greet in greetings):
        return "Hello 😊 How can I assist you today?"

    if any(t in q for t in thanks):
        return "You're welcome 😊 Let me know if you need any help!"

    return None

# GET ALL FILES 
@router.get("/files")
def get_files():
    files = os.listdir(KB_FOLDER)
    return files

# UPLOAD PDF
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(KB_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    add_pdf_to_kb(file_path)

    return {"message": "success"}

# DELETE PDF
@router.post("/delete/{filename}")
def delete_file(filename: str):
    file_path = os.path.join(KB_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

        # 🔥 remove from RAG
        remove_file_from_kb(file_path)

        return {"message": "Deleted"}

    return {"error": "File not found"}



@router.get("/ask")
def ask_question(query: str):
    print("QUERY RECEIVED:", query)
    small_talk = handle_small_talk(query)
    if small_talk:
        return {"answer": small_talk}

    # STEP 1: SEARCH FAQ
    faq_answer = search_faq(query)
    print("FAQ ANSWER:", faq_answer)

    # STEP 2: SEARCH PDF (RAG)
    chunks = search(query)
    context = "\n\n".join(chunks[:3]) if chunks else ""

    print("RAG CONTEXT:", context[:200])

    # STEP 3: NOTHING FOUND
    if not faq_answer and not context:
        return {"answer": "I couldn't find this information in our system.\n\n please raise a support ticket and our agent will assit you. "}

    final_prompt = f"""
You are a helpful support assistant.

User Question:
    {query}

FAQ Answer:
{faq_answer if faq_answer else "Not available"}

Knowledge Base:
{context if context else "Not available"}

Instructions:
- If FAQ answer is available, expand it clearly
- Add useful details from knowledge base
- Make the answer complete and easy to understand
- Do NOT just repeat the FAQ answer
- Give a proper explanation

Final Answer:
"""

    answer = generate_answer(query, final_prompt)
    answer = answer.replace("\n", " ").strip()
    print("Final Answer:", answer)

    if "CONTACT_AGENT" in answer.upper():
        return{
            "answer":"I'm not fully sure about this issue."
        }

    if len(answer) < 10:
        return {
    "answer": "I'm sorry, I couldn't find relevant information for your query in the knowledge base. 😊\n\nYou can raise a support ticket, and our agent will assist you shortly."
}

    return {"answer": answer}
