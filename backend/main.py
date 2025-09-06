from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend import llm
from backend.models import SessionLocal, InterviewSession

app = FastAPI(title="LLM Interview Backend")

# CORS (to allow frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for hackathon/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schemas
class GenerateRequest(BaseModel):
    role: str
    domain: str
    mode: str
    n: int

class EvaluateRequest(BaseModel):
    question: str
    answer: str
    mode: str

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.post("/generate")
def generate_questions(request: GenerateRequest):
    questions = llm.generate_questions(request.role, request.domain, request.mode, request.n)
    return {"questions": questions}

@app.post("/evaluate")
def evaluate_answer(request: EvaluateRequest):
    result = llm.evaluate_answer(request.question, request.answer, request.mode)

    # Save to DB
    db = SessionLocal()
    session_entry = InterviewSession(
        role="Unknown",   # could pass from frontend later
        domain="Unknown", # same here
        mode=request.mode,
        question=request.question,
        answer=request.answer,
        score=result["score"],
        feedback=result["feedback"]
    )
    db.add(session_entry)
    db.commit()
    db.close()

    return {"eval": result}

@app.get("/sessions")
def get_sessions():
    """Fetch all past interview sessions"""
    db = SessionLocal()
    sessions = db.query(InterviewSession).all()
    db.close()
    return sessions
