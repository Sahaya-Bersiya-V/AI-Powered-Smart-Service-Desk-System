
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User

router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all customers
@router.get("/")
def get_all_customers(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "customer").all()

# Update user status
@router.put("/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.get("status") not in ["active", "blocked"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    user.status = payload["status"]
    db.commit()

    return {
        "message": "Status updated",
        "status": user.status
    }

@router.put("/agents/{id}/status")
def update_agent_status(id: int, status: dict, db: Session = Depends(get_db)):
    agent = db.query(User).filter(User.id == id, User.role == "agent").first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = status["status"]
    db.commit()

    return {"message": "Status updated"}
@router.get("/agents")
def get_agents(db: Session = Depends(get_db)):
    agents = db.query(User).filter(User.role == "agent").all()

    return [
        {
            "id": a.id,
            "username": a.username,
            "email": a.email,
            "status": a.status
        }
        for a in agents
    ]