
from sentence_transformers import SentenceTransformer
import numpy as np
from database import get_db
from models.faq import FAQ

model = SentenceTransformer('all-MiniLM-L6-v2')


def search_faq(query: str):
    db = next(get_db())

    faqs = db.query(FAQ).all()

    if not faqs:
        return None

    questions = [faq.question for faq in faqs]

    # Convert to embeddings
    faq_embeddings = model.encode(questions)
    query_embedding = model.encode([query])

    # Compute similarity
    scores = np.dot(faq_embeddings, query_embedding.T).flatten()

    best_index = np.argmax(scores)
    best_score = scores[best_index]

    print("FAQ SCORE:", best_score)

    # threshold (important)
    if best_score > 0.5:
        return faqs[best_index].answer

    return None