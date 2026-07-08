from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import ai
import models
from database import engine, get_db

# Create the database tables if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Coding Tutor")


# --- Request body shapes ---

class LessonRequest(BaseModel):
    topic: str


class AnswerRequest(BaseModel):
    lesson_id: int
    user_code: str


# --- Routes ---

@app.post("/generate-lesson")
def generate_lesson(req: LessonRequest, db: Session = Depends(get_db)):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    try:
        lesson_text, exercise = ai.generate_lesson(req.topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    lesson = models.Lesson(
        topic=req.topic,
        lesson_text=lesson_text,
        exercise=exercise,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return {
        "lesson_id": lesson.id,
        "lesson": lesson_text,
        "exercise": exercise,
    }


@app.post("/check-answer")
def check_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == req.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    try:
        passed, feedback = ai.check_answer(lesson.exercise, req.user_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")

    submission = models.Submission(
        lesson_id=lesson.id,
        user_code=req.user_code,
        feedback=feedback,
        passed=passed,
    )
    db.add(submission)
    db.commit()

    return {"passed": passed, "feedback": feedback}


# --- Serve the frontend ---

@app.get("/")
def home():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
