from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from services.auth_service import hash_password

router = APIRouter(prefix="/admin/agents", tags=["Admin Agent"])


# CREATE AGENT
@router.post("/create")
def create_agent(username: str, email: str, password: str,department:str, db: Session = Depends(get_db)):

    # check existing
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    agent = User(
        username=username,
        email=email,
        password=hash_password(password),
        role="agent",
        status="active",
        department=department
    )

    db.add(agent)
    db.commit()

    return {"message": "Agent created successfully"}

@router.put("/update/{agent_id}")
def update_agent(
    agent_id: int,
    username: str,
    email: str,
    department: str,
    db: Session = Depends(get_db)
):
    agent = db.query(User).filter(User.id == agent_id, User.role == "agent").first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.username = username
    agent.email = email
    agent.department = department

    db.commit()

    return {"message": "Agent updated successfully"}

@router.put("/deactivate/{agent_id}")
def deactivate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(User).filter(User.id == agent_id, User.role == "agent").first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = "inactive"
    db.commit()

    return {"message": "Agent deactivated"}

@router.put("/activate/{agent_id}")
def activate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(User).filter(User.id == agent_id, User.role == "agent").first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.status = "active"
    db.commit()

    return {"message": "Agent activated"}