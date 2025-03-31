from fastapi import FastAPI, HTTPException
from aptos_sdk.account import Account
from aptos_sdk.transactions import TransactionPayload, EntryFunction
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, Optional

# Load environment variables
load_dotenv()

app = FastAPI()

# Set up Aptos connection
NODE_URL = "https://fullnode.devnet.aptoslabs.com"  # Use "testnet" or "mainnet" if needed

# Load your Aptos account
try:
    PRIVATE_KEY = os.getenv("APTOS_PRIVATE_KEY")
    if not PRIVATE_KEY:
        raise ValueError("APTOS_PRIVATE_KEY environment variable is not set")
    account = Account.load_key(PRIVATE_KEY)
except Exception as e:
    print(f"Error loading Aptos account: {str(e)}")
    account = None

# In-memory storage for student data (replace with database in production)
students: Dict[str, dict] = {}

class StudentRegistration(BaseModel):
    student_address: str

class RewardRequest(BaseModel):
    student_address: str
    amount: int

@app.get("/")
def home():
    if not account:
        raise HTTPException(status_code=500, detail="Aptos account not properly configured")
    return {"message": "Connected to Aptos Blockchain"}

@app.post("/register")
async def register_student(registration: StudentRegistration):
    try:
        student_address = registration.student_address
        if student_address in students:
            raise HTTPException(status_code=400, detail="Student already registered")
        
        students[student_address] = {
            "lessons_completed": 0,
            "total_rewards": 0
        }
        return {"message": "Student registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reward")
async def reward_student(reward: RewardRequest):
    try:
        student_address = reward.student_address
        amount = reward.amount
        
        if student_address not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Here you would implement the actual token transfer logic using Aptos SDK
        # For now, we'll just update the in-memory data
        students[student_address]["total_rewards"] += amount
        return {"message": f"Rewarded {amount} APT to student"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{address}")
async def check_progress(address: str):
    try:
        if address not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return students[address]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)