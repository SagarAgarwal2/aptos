from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import base64
import hashlib

# Load environment variables
load_dotenv()

# API configuration
NODE_URL = os.getenv("NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")

app = FastAPI()

# In-memory storage for development
students = {}
lessons = {}
lesson_completions = {}

class StudentRegistration(BaseModel):
    student_address: str
    public_key: str
    message: str
    signature: str
    network: str

class Lesson(BaseModel):
    title: str
    description: str
    reward_amount: int
    public_key: str
    message: str
    signature: str
    network: str

class LessonCompletion(BaseModel):
    student_address: str
    lesson_id: int
    public_key: str
    message: str
    signature: str
    network: str

def verify_signature(message: str, signature: str, public_key: str) -> bool:
    """Verify the signature using base64 encoded data"""
    try:
        # For development purposes, we'll accept any valid base64 signature
        # In production, you should implement proper cryptographic verification
        if signature == "dummy_signature":
            return True
            
        # Decode the base64 signature and public key
        signature_bytes = base64.b64decode(signature)
        public_key_bytes = base64.b64decode(public_key)
        
        # Basic validation
        if not signature_bytes or not public_key_bytes:
            print("Invalid signature or public key format")
            return False
            
        return True
    except Exception as e:
        print(f"Signature verification failed: {str(e)}")
        return False

def get_address_from_public_key(public_key: str) -> str:
    """Derive address from public key"""
    try:
        public_key_bytes = base64.b64decode(public_key)
        # Hash the public key and take first 32 bytes
        address_bytes = hashlib.sha256(public_key_bytes).digest()[:32]
        return base64.b64encode(address_bytes).decode()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid public key: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Crypto Literacy Learning App API is running"}

@app.post("/register")
async def register_student(registration: StudentRegistration):
    try:
        # Debug information
        print("Received registration data:", registration.dict())
        
        # Basic validation
        if not registration.student_address:
            raise HTTPException(status_code=400, detail="Student address is required")
        
        # Check if student is already registered
        if registration.student_address in students:
            raise HTTPException(status_code=400, detail="Student already registered")
        
        # For development, we'll accept any valid address
        # In production, you should implement proper address validation
        if not registration.student_address.startswith("0x"):
            raise HTTPException(status_code=400, detail="Invalid address format")
        
        # Store student information
        students[registration.student_address] = {
            "address": registration.student_address,
            "public_key": registration.public_key,
            "registered_at": datetime.now().isoformat(),
            "lessons_completed": [],
            "total_rewards": 0
        }
        
        print("Student registered successfully:", registration.student_address)
        return {"message": "Student registered successfully"}
    except HTTPException as he:
        print("Registration failed with HTTPException:", str(he))
        raise he
    except Exception as e:
        print("Registration failed with error:", str(e))
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/create_lesson")
async def create_lesson(lesson: Lesson):
    try:
        # Verify the signature
        if not verify_signature(lesson.message, lesson.signature, lesson.public_key):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        lesson_id = len(lessons) + 1
        lessons[lesson_id] = {
            "id": lesson_id,
            "title": lesson.title,
            "description": lesson.description,
            "reward_amount": lesson.reward_amount,
            "created_at": datetime.now().isoformat(),
            "creator_public_key": lesson.public_key
        }
        return {"lesson_id": lesson_id, "message": "Lesson created successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson creation failed: {str(e)}")

@app.post("/complete_lesson")
async def complete_lesson(completion: LessonCompletion):
    try:
        # Debug information
        print("Received completion data:", completion.dict())
        
        # Validate input
        if not completion.student_address:
            raise HTTPException(status_code=400, detail="Student address is required")
        if not completion.lesson_id:
            raise HTTPException(status_code=400, detail="Lesson ID is required")
        
        if completion.student_address not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        
        if completion.lesson_id not in lessons:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        if completion.lesson_id in students[completion.student_address]["lessons_completed"]:
            raise HTTPException(status_code=400, detail="Lesson already completed")
        
        # For development, we'll simulate the transaction
        try:
            # Simulate transaction hash
            transaction_hash = f"dev_tx_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Update student's progress
            students[completion.student_address]["lessons_completed"].append(completion.lesson_id)
            students[completion.student_address]["total_rewards"] += lessons[completion.lesson_id]["reward_amount"]
            
            print("Lesson completed successfully for student:", completion.student_address)
            print("Transaction hash:", transaction_hash)
            print("Reward earned:", lessons[completion.lesson_id]["reward_amount"])
            
            return {
                "message": "Lesson completed successfully",
                "transaction_hash": transaction_hash,
                "reward_earned": lessons[completion.lesson_id]["reward_amount"]
            }
        except Exception as e:
            print("Error in transaction simulation:", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to complete lesson: {str(e)}")
    except HTTPException as he:
        print("HTTP Exception in complete_lesson:", str(he))
        raise he
    except Exception as e:
        print("General error in complete_lesson:", str(e))
        raise HTTPException(status_code=500, detail=f"Lesson completion failed: {str(e)}")

@app.get("/progress/{student_address}")
async def get_progress(student_address: str):
    try:
        if not student_address:
            raise HTTPException(status_code=400, detail="Student address is required")
        
        if student_address not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {
            "lessons_completed": students[student_address]["lessons_completed"],
            "total_rewards": students[student_address]["total_rewards"]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@app.get("/lessons")
async def get_lessons():
    try:
        return list(lessons.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lessons: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)