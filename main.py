from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from functools import partial
import asyncio

from database import get_db, User, Event, Complaint, init_db
from auth import hash_password, verify_password, create_token, get_current_user
from cloudinary_helper import upload_image
import os
from dotenv import load_dotenv
load_dotenv()

ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "admin@hub.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")

app = FastAPI(title="Smart Community Hub")

# Create DB tables on startup
init_db()

# Auto-create admin account if it doesn't exist
def seed_admin():
    db = next(get_db())
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not existing:
        admin = User(
            name="Admin",
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        print(f"[startup] Admin account created → {ADMIN_EMAIL}")
    elif not existing.is_admin:
        existing.is_admin = True
        db.commit()
        print(f"[startup] Existing user {ADMIN_EMAIL} promoted to admin")

seed_admin()

# Serve frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


# ── AUTH ──────────────────────────────────────────────────────────────────────

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str

class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/auth/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        is_admin=(body.email.lower() == ADMIN_EMAIL.lower()),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_token(user.email), "name": user.name, "is_admin": user.is_admin}


@app.post("/auth/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(user.email), "name": user.name, "is_admin": user.is_admin}


# ── EVENTS ────────────────────────────────────────────────────────────────────

@app.get("/events")
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "date": e.date,
            "time": e.time,
            "image_url": e.image_url,
            "posted_by": e.owner.name,
        }
        for e in events
    ]


@app.post("/events")
async def create_event(
    title: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = None
    if image and image.filename:
        contents = await image.read()          # read fully into memory first
        loop = asyncio.get_event_loop()
        image_url = await loop.run_in_executor(None, partial(upload_image, contents))

    event = Event(user_id=current_user.id, title=title, date=date, time=time, image_url=image_url)
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"id": event.id, "title": event.title, "image_url": event.image_url}


# ── COMPLAINTS ────────────────────────────────────────────────────────────────

@app.get("/complaints")
def get_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        complaints = db.query(Complaint).all()
    else:
        complaints = db.query(Complaint).filter(Complaint.user_id == current_user.id).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "image_url": c.image_url,
            "status": c.status,
            "resolve_reason": c.resolve_reason,
            "posted_by": c.owner.name,
        }
        for c in complaints
    ]


class StatusUpdate(BaseModel):
    status: str           # "pending" | "in_review" | "resolved"
    resolve_reason: Optional[str] = None


@app.patch("/complaints/{complaint_id}/status")
def update_complaint_status(
    complaint_id: int,
    body: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can resolve complaints")
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if body.status == "resolved" and not body.resolve_reason:
        raise HTTPException(status_code=400, detail="A resolve reason is required")
    complaint.status = body.status
    complaint.resolve_reason = body.resolve_reason
    db.commit()
    return {"id": complaint.id, "status": complaint.status}


@app.post("/complaints")
async def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = None
    if image and image.filename:
        contents = await image.read()          # read fully into memory first
        loop = asyncio.get_event_loop()
        image_url = await loop.run_in_executor(None, partial(upload_image, contents))

    complaint = Complaint(
        user_id=current_user.id,
        title=title,
        description=description,
        image_url=image_url,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return {"id": complaint.id, "title": complaint.title}


# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7979, reload=True)
