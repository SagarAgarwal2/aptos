from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# In-memory storage for students and lessons
students: Dict[str, dict] = {}
lessons: List[dict] = []

class StudentRegistration(BaseModel):
    student_address: str

class LessonCreation(BaseModel):
    title: str
    description: str
    reward_amount: int

class CompleteLesson(BaseModel):
    student_address: str
    lesson_id: int

@app.get("/")
def home():
    return {"message": "Crypto Literacy Learning App API is running"}

@app.post("/register")
async def register_student(registration: StudentRegistration):
    student_address = registration.student_address

    if student_address in students:
        raise HTTPException(status_code=400, detail="Student already registered")
    
    students[student_address] = {
        "lessons_completed": [],
        "total_rewards": 0
    }
    
    return {"message": "Student registered successfully"}

@app.post("/create_lesson")
async def create_lesson(lesson: LessonCreation):
    lesson_id = len(lessons)
    lessons.append({
        "id": lesson_id,
        "title": lesson.title,
        "description": lesson.description,
        "reward_amount": lesson.reward_amount
    })
    
    return {"message": "Lesson created successfully", "lesson_id": lesson_id}

@app.post("/complete_lesson")
async def complete_lesson(request: CompleteLesson):
    student_address = request.student_address
    lesson_id = request.lesson_id

    if student_address not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if lesson_id >= len(lessons):
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson_id in students[student_address]["lessons_completed"]:
        raise HTTPException(status_code=400, detail="Lesson already completed")
    
    students[student_address]["lessons_completed"].append(lesson_id)
    students[student_address]["total_rewards"] += lessons[lesson_id]["reward_amount"]

    return {"message": f"Lesson {lesson_id} completed. Reward earned: {lessons[lesson_id]['reward_amount']} APT"}

@app.get("/progress/{student_address}")
async def check_progress(student_address: str):
    if student_address not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return students[student_address]

@app.get("/lessons")
async def get_lessons():
    return lessons

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
