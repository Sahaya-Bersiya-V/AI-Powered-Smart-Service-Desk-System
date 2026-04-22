

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from database import engine, Base, SessionLocal
from models import user, faq
from models.user import User
from routers.auth_router import router as auth_router
from routers.faq_router import router as faq_router
from routers.kb_router import router as kb_router
from routers.admin_user_router import router as admin_user_router
from services.auth_service import hash_password
from routers.admin_faq_router import router as admin_faq_router
from routers.ticket_router import router as ticket_router
from routers.admin_agent_router import router as admin_agent_router

# APP INIT
app = FastAPI()

# DATABASE
Base.metadata.create_all(bind=engine)


# ROUTERS
app.include_router(auth_router)
app.include_router(faq_router)
app.include_router(admin_user_router)
app.include_router(admin_faq_router)
app.include_router(kb_router)
app.include_router(ticket_router)
app.include_router(admin_agent_router)

# STATIC & TEMPLATES
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# PUBLIC PAGES
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# DASHBOARDS
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/agent", response_class=HTMLResponse)
def agent_dashboard(request: Request):
    return templates.TemplateResponse("agent.html", {"request": request})


@app.get("/customer", response_class=HTMLResponse)
def customer_dashboard(request: Request):
    return templates.TemplateResponse("customer.html", {"request": request})

@app.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request):
    return templates.TemplateResponse("admin_user.html", {"request": request})

@app.get("/admin/faqs", response_class=HTMLResponse)
def admin_faqs(request: Request):
    return templates.TemplateResponse("admin_faq.html", {"request": request})

UPLOAD_FOLDER = "uploads"


@app.get("/admin/rag", response_class=HTMLResponse)
def kb_management(request: Request):
    files = os.listdir(UPLOAD_FOLDER) if os.path.exists(UPLOAD_FOLDER) else []
    
    return templates.TemplateResponse("admin_kb.html", {
        "request": request,
        "files": files
    })

# DEFAULT USERS
def create_default_users():
    db = SessionLocal()

    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(
            username="admin",
            email="admin@system.com",
            password=hash_password("admin123"),
            role="admin"
        ))

    if not db.query(User).filter(User.username == "agent").first():
        db.add(User(
            username="agent",
            email="agent@system.com",
            password=hash_password("agent123"),
            role="agent"
        ))

    db.commit()
    db.close()

create_default_users()




