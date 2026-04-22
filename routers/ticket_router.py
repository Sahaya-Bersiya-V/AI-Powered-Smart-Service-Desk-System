from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.ticket import Ticket
from services.ai_service import analyze_ticket
router = APIRouter(prefix="/tickets", tags=["Tickets"])
from services.ai_service import analyze_ticket
from fastapi import UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
from services.ai_summary import generate_summary, generate_ticket_summary

from services.file_ai import extract_text
from services.ai_summary import generate_summary
from models.ticket import Ticket
from database import get_db
from datetime import datetime, date



@router.post("/create")
async def create_ticket(
    user_id: int = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    summary = None
    attachment = None
    # FILE PROCESSING
    if file and file.filename:
        os.makedirs("uploads", exist_ok=True)

        file_path = f"uploads/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        attachment = file.filename  

        try:
            extracted_text = extract_text(file_path, file.filename)

            #Summary from file
            summary = generate_summary(extracted_text)

        except Exception as e:
            print("FILE AI ERROR:", e)
            summary = "Unable to process file"

    else:
        #SUMMARY FROM SUBJECT + DESCRIPTION
        try:
            summary = generate_ticket_summary(subject, description)
        except Exception as e:
            print("TEXT SUMMARY ERROR:", e)
            summary = "Summary not available"

    # CREATE TICKET
    queue = detect_queue(subject)
    priority = detect_priority(description)

    ticket = Ticket(
        user_id=user_id,
        subject=subject,
        description=description,
        summary=summary,
        attachment=attachment,
        queue=queue,
        priority=priority,
        status="open"
    )

    db.add(ticket)
    db.commit()

    return {"message": "Ticket created successfully"}

@router.get("/all")
def get_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()

    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "subject": t.subject,
            "description": t.description,
            "status": t.status,
            "reply": t.reply,
            "queue": t.queue,
            "priority": t.priority,
            "summary": t.summary
        }
        for t in tickets
    ]


@router.put("/reply/{ticket_id}")
def reply_ticket(ticket_id: int, reply: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.reply = reply
    ticket.status = "resolved"

    db.commit()

    return {"message": "Reply sent"}

def detect_queue(subject):
    if "login" in subject.lower():
        return "IT"
    elif "salary" in subject.lower():
        return "HR"
    return "Facilities"

def detect_priority(description):
    if "urgent" in description.lower():
        return "High"
    elif "slow" in description.lower():
        return "Low"
    return "Medium"

@router.get("/agent/{department}")
def get_agent_tickets(department: str, db: Session = Depends(get_db)):
    
    tickets = db.query(Ticket).filter(Ticket.queue == department).all()

    return [
        {
            "id": t.id,
            "subject": t.subject,
            "description":t.description,
            "priority": t.priority,
            "status": t.status,
            "queue": t.queue,
            "reply":t.reply,
            "summary":t.summary

        }
        for t in tickets
    ]

@router.get("/dashboard/{department}")
def agent_dashboard(department: str, db: Session = Depends(get_db)):

    tickets = db.query(Ticket).filter(Ticket.queue == department).all()

    today = date.today()

    total = len(tickets)
    open_tickets = len([t for t in tickets if t.status == "open"])
    closed_tickets = len([t for t in tickets if t.status == "resolved"])

    today_tickets = len([
        t for t in tickets 
        if t.created_at and t.created_at.date() == today
    ])

    return {
        "total": total,
        "open": open_tickets,
        "closed": closed_tickets,
        "today": today_tickets
    }
from typing import Optional
from fastapi import Query
@router.get("/filter")
def filter_tickets(department: str, priority: Optional[str]=Query(None), db: Session = Depends(get_db)):
    query = db.query(Ticket).filter(Ticket.queue == department)

    if priority is not None and priority != "":
        query = query.filter(Ticket.priority == priority)
    tickets = query.all()

    return [
        {
        "id": t.id,
        "subject": t.subject,
        "description":t.description,
        "priority": t.priority,
        "status": t.status,
        "queue":t.queue,
        "reply":t.reply,
        "summary":t.summary
        }
        for t in tickets
    ]
@router.get("/{user_id}")
def get_user_tickets(user_id: int, db: Session = Depends(get_db)):
    tickets = db.query(Ticket).filter(Ticket.user_id == user_id).all()

    return [
        {
            "id": t.id,
            "subject": t.subject,
            "description": t.description,
            "status": t.status,
            "reply": t.reply
        }
        for t in tickets
    ]
