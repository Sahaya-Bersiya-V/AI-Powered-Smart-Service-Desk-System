import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import os
import pickle
from services.file_ai import extract_text

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Storage paths
FAISS_INDEX_PATH = "faiss_index.index"
CHUNKS_PATH = "chunks.pkl"

# Load or initialize
if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
else:
    index = faiss.IndexFlatL2(384)
    chunks = []

#extract text from pdf

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    print("TEXT:", text[:500])

    for page in reader.pages:
       
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

import re

def split_text(text, chunk_size=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# ADD PDF TO KB

def add_pdf_to_kb(file_path):
    global index, chunks
    filename=os.path.basename(file_path)

    text = extract_text(file_path,filename)
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = re.sub(r'(\w)\s+(\w)', r'\1\2', text)
    text = re.sub(r'(\w)\s+([a-z])', r'\1\2', text)
    text = re.sub(r'\s+', ' ', text).strip()
    new_chunks = split_text(text)

    embeddings = model.encode(new_chunks)

    index.add(np.array(embeddings))
    for chunk in new_chunks:
        chunks.append({
            "text": chunk,
            "source": file_path
        })
    print("CHUNKS CREATED:", len(new_chunks))

    # Save
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

def search(query, k=5):
    global index, chunks

    if index is None or len(chunks) == 0:
        return []

    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")  

    distances, indices = index.search(query_embedding, k)

    results = []
    query_words = query.lower().split()

    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):

        
            text = chunks[idx]["text"]

            match_count = sum(word in text.lower() for word in query_words)

            if match_count >= 2:  
                results.append(text)

    # fallback
    if not results:
        for idx in indices[0][:3]:
            if idx < len(chunks):
                results.append(chunks[idx]["text"])

    print("TOP CHUNKS:")
    for r in results:
        print(r[:100])

    return results[:3]
def clear_kb():
    global index, chunks

    index = faiss.IndexFlatL2(384)  
    chunks = []                     

    # delete saved files
    if os.path.exists(FAISS_INDEX_PATH):
        os.remove(FAISS_INDEX_PATH)

    if os.path.exists(CHUNKS_PATH):
        os.remove(CHUNKS_PATH)

def remove_file_from_kb(file_path):
    global index, chunks

    # keep only other files
    remaining_chunks = [c for c in chunks if c["source"] != file_path]

    # rebuild index
    index = faiss.IndexFlatL2(384)

    if remaining_chunks:
        texts = [c["text"] for c in remaining_chunks]
        embeddings = model.encode(texts)
        index.add(np.array(embeddings))

    chunks = remaining_chunks

    # save again
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

