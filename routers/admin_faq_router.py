
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.faq import FAQ

router = APIRouter(prefix="/admin/faq", tags=["Admin FAQ"])

# Get all FAQs
@router.get("/")
def get_faqs(db: Session = Depends(get_db)):
    return db.query(FAQ).all()


# Add FAQ
@router.post("/")
def add_faq(question: str, answer: str, db: Session = Depends(get_db)):
    new_faq = FAQ(question=question, answer=answer)
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return {"message": "FAQ added successfully"}


# Update FAQ
@router.put("/{faq_id}")
def update_faq(faq_id: int, question: str, answer: str, db: Session = Depends(get_db)):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()

    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    faq.question = question
    faq.answer = answer
    db.commit()

    return {"message": "FAQ updated successfully"}


# Delete FAQ
@router.delete("/{faq_id}")
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()

    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")

    db.delete(faq)
    db.commit()

    return {"message": "FAQ deleted successfully"}