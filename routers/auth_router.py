
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import re
from database import get_db
from models.user import User
from schemas.user import LoginRequest
from services.auth_service import hash_password, verify_password

router = APIRouter()
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@router.post("/register/customer")
def register_customer(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Email format validation
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid email address"
        )

    # Password length validation
    if len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long"
        )

    # Username already exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already exists. Please choose another one."
        )

    # Email already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login or use another email."
        )

    # Create user
    new_user = User(
        username=username,
        email=email,
        password=hash_password(password),
        role="customer"
    )

    db.add(new_user)
    db.commit()

   
    return JSONResponse({
    "message": "Registration successful",
    "user_id": new_user.id,
    "username": new_user.username,
    "role": new_user.role
})



from fastapi import HTTPException

@router.post("/login")
def login(data:LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()
    from services.auth_service import verify_password

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Account deactivated by admin")

    return {
        "message": "Login success",
        "user_id":user.id,
        "username":user.username,
        "role": user.role,
        "department": user.department  
    }
