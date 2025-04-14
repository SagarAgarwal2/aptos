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
from aptos_sdk.account import Account
from aptos_sdk.transactions import TransactionPayload, EntryFunction, TransactionArgument
from aptos_sdk.async_client import RestClient, FaucetClient
import json

# Load environment variables
load_dotenv()

# API configuration
NODE_URL = os.getenv("NODE_URL", "https://fullnode.devnet.aptoslabs.com")
FAUCET_URL = os.getenv("FAUCET_URL", "https://faucet.devnet.aptoslabs.com")
MODULE_ADDRESS = os.getenv("MODULE_ADDRESS", "your_module_address")
MODULE_NAME = os.getenv("MODULE_NAME", "LearningApp")

app = FastAPI()

# Initialize Aptos clients
client = RestClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, client)

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
    """Verify the signature using the public key"""
    try:
        # In production, implement proper signature verification
        # For now, we'll accept any valid signature
        return True
    except Exception as e:
        print(f"Signature verification failed: {str(e)}")
        return False

def get_address_from_public_key(public_key: str) -> str:
    """Derive address from public key"""
    try:
        # In production, implement proper address derivation
        # For now, we'll use the public key as the address
        return public_key
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid public key: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Crypto Literacy Learning App API is running"}

@app.post("/register")
async def register_student(registration: StudentRegistration):
    try:
        # Debug information
        print("Received registration data:", registration.model_dump())
        
        # Basic validation
        if not registration.student_address:
            raise HTTPException(status_code=400, detail="Student address is required")
        
        # Create transaction payload
        payload = TransactionPayload(
            EntryFunction.natural(
                f"{MODULE_ADDRESS}::{MODULE_NAME}",
                "register_student",
                [],
                []
            )
        )
        
        # Submit transaction
        try:
            # Ensure private key has 0x prefix
            private_key = registration.public_key
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            
            # Create account from private key
            account = Account.load_key(private_key)
            
            # Submit transaction
            txn_hash = client.submit_transaction(account, payload)
            
            return {
                "message": "Student registered successfully",
                "transaction_hash": txn_hash
            }
        except Exception as e:
            print("Transaction failed:", str(e))
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except HTTPException as he:
        print("Registration failed with HTTPException:", str(he))
        raise he
    except Exception as e:
        print("Registration failed with error:", str(e))
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/create_lesson")
async def create_lesson(lesson: Lesson):
    try:
        # Create transaction payload
        payload = TransactionPayload(
            EntryFunction.natural(
                f"{MODULE_ADDRESS}::{MODULE_NAME}",
                "create_lesson",
                [],
                [
                    TransactionArgument(lesson.title, "String"),
                    TransactionArgument(lesson.description, "String"),
                    TransactionArgument(lesson.reward_amount, "U64")
                ]
            )
        )
        
        # Submit transaction
        try:
            # Create account from private key
            account = Account.load_key(lesson.public_key)
            
            # Submit transaction
            txn_hash = client.submit_transaction(account, payload)
            
            return {
                "message": "Lesson created successfully",
                "transaction_hash": txn_hash
            }
        except Exception as e:
            print("Transaction failed:", str(e))
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson creation failed: {str(e)}")

@app.post("/complete_lesson")
async def complete_lesson(completion: LessonCompletion):
    try:
        # Debug information
        print("Received completion data:", completion.model_dump())
        
        # Validate input
        if not completion.student_address:
            raise HTTPException(status_code=400, detail="Student address is required")
        if not completion.lesson_id:
            raise HTTPException(status_code=400, detail="Lesson ID is required")
        
        # Create transaction payload
        payload = TransactionPayload(
            EntryFunction.natural(
                f"{MODULE_ADDRESS}::{MODULE_NAME}",
                "complete_lesson",
                [],
                [
                    TransactionArgument(completion.lesson_id, "U64")
                ]
            )
        )
        
        # Submit transaction
        try:
            # Create account from private key
            account = Account.load_key(completion.public_key)
            
            # Submit transaction
            txn_hash = client.submit_transaction(account, payload)
            
            return {
                "message": "Lesson completed successfully",
                "transaction_hash": txn_hash
            }
        except Exception as e:
            print("Transaction failed:", str(e))
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
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
        
        # Get account resources
        resources = client.account_resources(student_address)
        
        # Find the student resource
        student_resource = next(
            (r for r in resources if r["type"] == f"{MODULE_ADDRESS}::{MODULE_NAME}::Student"),
            None
        )
        
        if student_resource:
            return {
                "lessons_completed": student_resource["data"]["lessons_completed"],
                "total_rewards": student_resource["data"]["total_rewards"]
            }
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@app.get("/lessons")
async def get_lessons():
    try:
        # Get module resources
        resources = client.account_resources(MODULE_ADDRESS)
        
        # Find all lesson resources
        lessons = [
            r for r in resources 
            if r["type"].startswith(f"{MODULE_ADDRESS}::{MODULE_NAME}::Lesson")
        ]
        
        return lessons
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lessons: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
