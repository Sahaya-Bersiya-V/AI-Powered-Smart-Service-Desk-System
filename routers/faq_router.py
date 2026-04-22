from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.faq import FAQ

router = APIRouter(prefix="/faqs", tags=["FAQs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET ALL FAQs
@router.get("/")
def get_faqs(db: Session = Depends(get_db)):
    return db.query(FAQ).all()
