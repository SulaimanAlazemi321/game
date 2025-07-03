"""FastAPI Reflection Journal App
A simple web app that shows a random reflection question and stores the user's answer
in an SQLite database using SQLAlchemy.
Run with:
    uvicorn fastapi_reflection_app:app --reload
"""

import random
from datetime import datetime

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./reflections.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------------ Models ---------------------------------
class ReflectionQuestion(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, unique=True, nullable=False)

    answers = relationship("ReflectionAnswer", back_populates="question")


class ReflectionAnswer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("ReflectionQuestion", back_populates="answers")


# --------------------------- Pydantic Schemas ---------------------------
class AnswerCreate(BaseModel):
    question_id: int
    answer_text: str


class AnswerOut(BaseModel):
    id: int
    question_id: int
    answer_text: str
    created_at: datetime

    class Config:
        orm_mode = True


# --------------------------- FastAPI Setup ------------------------------
app = FastAPI(title="Reflection Journal")

templates = Jinja2Templates(directory="templates")

# -------------------------- Dependency ----------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------- Utility ------------------------------------
DEFAULT_QUESTIONS = [
    "How was your day?",
    "What is one thing you are grateful for today?",
    "What is your plan for tomorrow?",
    "Which personal value guided you today?",
    "How are your relationships this week?",
]


def init_db():
    """Create tables and ensure default questions exist."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(ReflectionQuestion).count() == 0:
            for q in DEFAULT_QUESTIONS:
                db.add(ReflectionQuestion(text=q))
            db.commit()
    finally:
        db.close()


init_db()

# --------------------------- Routes --------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Serve an HTML page with a random question and answer form."""
    question = random.choice(db.query(ReflectionQuestion).all())
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
        },
    )


@app.post("/submit", response_class=RedirectResponse)
async def submit_answer(
    question_id: int = Form(...),
    answer_text: str = Form(...),
    db: Session = Depends(get_db),
):
    if not answer_text.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")

    db_answer = ReflectionAnswer(question_id=question_id, answer_text=answer_text.strip())
    db.add(db_answer)
    db.commit()

    # Redirect back to home to show a new question
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/random-question", response_model=AnswerOut)
async def api_random_question(db: Session = Depends(get_db)):
    """API endpoint to get a random question (JSON)."""
    question = random.choice(db.query(ReflectionQuestion).all())
    return {"id": question.id, "question_id": question.id, "answer_text": question.text, "created_at": datetime.utcnow()}


@app.post("/api/answer", response_model=AnswerOut)
async def api_create_answer(answer: AnswerCreate, db: Session = Depends(get_db)):
    db_answer = ReflectionAnswer(**answer.dict())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer
