

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey,Text
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(255))
    description = Column(String(1000))
    status = Column(String(50), default="open")
    queue = Column(String(50))
    priority = Column(String(20))

    attachment = Column(String(255))
    summary = Column(Text)

    reply = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
