from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import uuid
from datetime import datetime
from blockchain import BlockchainManager

app = FastAPI()

# Initialize blockchain manager
blockchain = BlockchainManager()

# Data models
class Student(BaseModel):
    address: str
    lessons_completed: List[int] = []
    total_rewards: int = 0

class Lesson(BaseModel):
    id: int
    title: str
    description: str
    reward_amount: int

class CompleteLessonRequest(BaseModel):
    student_address: str
    lesson_id: int
    sender_address: str
    private_key: Optional[str] = None

class WalletConnection(BaseModel):
    address: str
    private_key: Optional[str] = None

# In-memory storage (replace with database in production)
students = {}
lessons = {}
wallet_connections = {}

# Helper functions
def generate_transaction_hash():
    return f"0x{uuid.uuid4().hex}"

# API endpoints
@app.post("/connect_wallet")
async def connect_wallet(wallet: WalletConnection):
    """Connect a wallet to the application."""
    wallet_connections[wallet.address] = {
        "connected_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "private_key": wallet.private_key
    }
    return {"status": "connected", "address": wallet.address}

@app.post("/register")
async def register_student(student: Student):
    """Register a new student."""
    if student.address in students:
        raise HTTPException(status_code=400, detail="Student already registered")
    
    # Check if we have a private key for this address
    private_key = None
    if student.address in wallet_connections and wallet_connections[student.address].get("private_key"):
        private_key = wallet_connections[student.address]["private_key"]
    
    # Register on blockchain
    blockchain_result = blockchain.register_student(student.address, private_key)
    
    if not blockchain_result["success"]:
        # If blockchain registration fails, still register in our local storage
        students[student.address] = student.dict()
        return {"status": "registered", "address": student.address, "blockchain_status": "failed", "error": blockchain_result.get("error")}
    
    # Register in local storage
    students[student.address] = student.dict()
    
    return {
        "status": "registered", 
        "address": student.address,
        "blockchain_status": "success",
        "transaction_hash": blockchain_result.get("transaction_hash")
    }

@app.post("/create_lesson")
async def create_lesson(lesson: Lesson):
    """Create a new lesson."""
    if lesson.id in lessons:
        raise HTTPException(status_code=400, detail="Lesson ID already exists")
    
    # Get admin private key (in a real app, this would be securely stored)
    admin_private_key = os.environ.get("ADMIN_PRIVATE_KEY")
    
    # Create on blockchain
    blockchain_result = blockchain.create_lesson(
        lesson.title, 
        lesson.description, 
        lesson.reward_amount,
        admin_private_key
    )
    
    if not blockchain_result["success"]:
        # If blockchain creation fails, still create in our local storage
        lessons[lesson.id] = lesson.dict()
        return {"status": "created", "lesson_id": lesson.id, "blockchain_status": "failed", "error": blockchain_result.get("error")}
    
    # Create in local storage
    lessons[lesson.id] = lesson.dict()
    
    return {
        "status": "created", 
        "lesson_id": lesson.id,
        "blockchain_status": "success",
        "transaction_hash": blockchain_result.get("transaction_hash")
    }

@app.post("/complete_lesson")
async def complete_lesson(request: CompleteLessonRequest):
    """Complete a lesson and transfer rewards."""
    # Check if student exists
    if request.student_address not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if lesson exists
    if request.lesson_id not in lessons:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if lesson already completed
    if request.lesson_id in students[request.student_address]["lessons_completed"]:
        raise HTTPException(status_code=400, detail="Lesson already completed")
    
    # Get lesson details
    lesson = lessons[request.lesson_id]
    
    # Get private key for sender
    private_key = request.private_key
    if not private_key and request.sender_address in wallet_connections:
        private_key = wallet_connections[request.sender_address].get("private_key")
    
    # Complete on blockchain
    blockchain_result = blockchain.complete_lesson(
        request.student_address,
        request.lesson_id,
        request.sender_address,
        private_key
    )
    
    if not blockchain_result["success"]:
        # If blockchain completion fails, still complete in our local storage
        transaction_hash = generate_transaction_hash()
        
        # Update student progress
        students[request.student_address]["lessons_completed"].append(request.lesson_id)
        students[request.student_address]["total_rewards"] += lesson["reward_amount"]
        
        return {
            "status": "completed",
            "transaction_hash": transaction_hash,
            "reward_amount": lesson["reward_amount"],
            "blockchain_status": "failed",
            "error": blockchain_result.get("error")
        }
    
    # Update student progress
    students[request.student_address]["lessons_completed"].append(request.lesson_id)
    students[request.student_address]["total_rewards"] += lesson["reward_amount"]
    
    return {
        "status": "completed",
        "transaction_hash": blockchain_result.get("transaction_hash"),
        "reward_amount": lesson["reward_amount"],
        "blockchain_status": "success"
    }

@app.get("/lessons")
async def get_lessons():
    """Get all lessons."""
    return list(lessons.values())

@app.get("/progress/{student_address}")
async def get_progress(student_address: str):
    """Get student progress."""
    if student_address not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get blockchain data
    blockchain_result = blockchain.get_student_progress(student_address)
    
    if blockchain_result["success"]:
        # Merge blockchain data with local data
        local_data = students[student_address]
        blockchain_data = blockchain_result["data"]
        
        # Use blockchain data if available, otherwise use local data
        return {
            "address": student_address,
            "lessons_completed": blockchain_data.get("lessons_completed", local_data["lessons_completed"]),
            "total_rewards": blockchain_data.get("total_rewards", local_data["total_rewards"]),
            "blockchain_status": "success"
        }
    
    # If blockchain data not available, use local data
    return {
        "address": student_address,
        "lessons_completed": students[student_address]["lessons_completed"],
        "total_rewards": students[student_address]["total_rewards"],
        "blockchain_status": "failed",
        "error": blockchain_result.get("error")
    }

@app.get("/blockchain/student/{student_address}")
async def get_blockchain_data(student_address: str):
    """Get student data from the blockchain."""
    # Get blockchain data
    blockchain_result = blockchain.get_student_progress(student_address)
    
    if blockchain_result["success"]:
        return {
            "address": student_address,
            "lessons_completed": blockchain_result["data"].get("lessons_completed", []),
            "total_rewards": blockchain_result["data"].get("total_rewards", 0),
            "blockchain_status": "success"
        }
    
    # If blockchain data not available, use local data
    if student_address in students:
        return {
            "address": student_address,
            "lessons_completed": students[student_address]["lessons_completed"],
            "total_rewards": students[student_address]["total_rewards"],
            "blockchain_status": "failed",
            "error": blockchain_result.get("error")
        }
    
    raise HTTPException(status_code=404, detail="Student not found") 