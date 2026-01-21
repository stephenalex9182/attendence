from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base, SessionLocal
from .routers import auth, attendance, users, courses
from . import models, auth as auth_utils

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
origins = ["*"] # Allow all for now, or specific frontend port
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendance.router)
app.include_router(courses.router)

# ... imports
import os

# ...

# Serve Static Files
# Resolve paths relative to this file (backend/main.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{filename}.html")
def read_html(filename: str):
    return FileResponse(os.path.join(FRONTEND_DIR, f"{filename}.html"))

@app.on_event("startup")
def startup_event():
    # Seed Faculty User
    db = SessionLocal()
    faculty_email = "ruthiwic@mlrit.ac.in"
    user = db.query(models.User).filter(models.User.email == faculty_email).first()
    if not user:
        hashed_password = auth_utils.get_password_hash("password123")
        faculty = models.User(
            email=faculty_email,
            hashed_password=hashed_password,
            role="faculty"
        )
        db.add(faculty)
        db.commit()
        print(f"Created faculty user: {faculty_email}")
    db.close()
