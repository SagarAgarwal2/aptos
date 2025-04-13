from fastapi import FastAPI, HTTPException
from aptos_sdk.account import Account
from aptos_sdk.transactions import TransactionPayload, EntryFunction
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict
from aptos_sdk.type_tag import StructTag
import requests
import json
import time  # Add time import
from aptos_sdk.rest_client import RestClient
from nacl.signing import SigningKey
from nacl.public import VerifyKey

# Load environment variables
load_dotenv()

app = FastAPI()

# Set up Aptos connection
NODE_URL = "https://fullnode.devnet.aptoslabs.com"  # Use "testnet" or "mainnet" if needed

# Initialize Aptos client
try:
    client = RestClient(NODE_URL)
except Exception as e:
    print(f"Error initializing Aptos client: {str(e)}")
    client = None

# Load your Aptos account
try:
    PRIVATE_KEY = os.getenv("APTOS_PRIVATE_KEY")
    if not PRIVATE_KEY:
        raise ValueError("APTOS_PRIVATE_KEY environment variable is not set")
    
    # Convert private key to bytes if it's in hex format
    if PRIVATE_KEY.startswith("0x"):
        PRIVATE_KEY = PRIVATE_KEY[2:]
    private_key_bytes = bytes.fromhex(PRIVATE_KEY)
    
    # Create signing key from bytes
    signing_key = SigningKey(private_key_bytes)
    verify_key = signing_key.verify_key
    
    # Create Aptos account with the signing key
    account = Account(signing_key, verify_key)
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
    sender_address: str

@app.get("/")
def home():
    if not account:
        raise HTTPException(status_code=500, detail="Aptos account not properly configured")
    return {"message": "Connected to Aptos Blockchain"}

@app.post("/register")
async def register_student(registration: StudentRegistration):
    try:
        student_address = registration.student_address
        if not student_address.startswith("0x"):
            student_address = "0x" + student_address
            
        if student_address in students:
            raise HTTPException(status_code=400, detail="Student already registered")
        
        students[student_address] = {
            "lessons_completed": 0,
            "total_rewards": 0
        }
        return {"message": "Student registered successfully"}
    except Exception as e:
        print(f"Error in registration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reward")
async def reward_student(reward: RewardRequest):
    try:
        if not account:
            raise HTTPException(status_code=500, detail="Aptos account not properly configured")
            
        student_address = reward.student_address
        amount = reward.amount
        sender_address = reward.sender_address
        
        # Ensure addresses start with 0x
        if not student_address.startswith("0x"):
            student_address = "0x" + student_address
        if not sender_address.startswith("0x"):
            sender_address = "0x" + sender_address
        
        if student_address not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Create the transfer transaction payload
        txn_payload = {
            "function": "0x1::Coin::transfer",
            "type_arguments": ["0x1::aptos_coin::AptosCoin"],
            "arguments": [student_address, str(amount)]
        }

        # Submit transaction to Aptos
        txn_response = submit_transaction(txn_payload)

        return {"message": "Reward sent successfully", "transaction": txn_response}
    except Exception as e:
        print(f"Error in reward transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending reward: {str(e)}")

def submit_transaction(payload):
    """Submit a transaction to Aptos."""
    transaction = {
        "sender": account.address(),
        "sequence_number": str(get_account_sequence()),
        "max_gas_amount": "1000",
        "gas_unit_price": "1",
        "expiration_timestamp_secs": str(int(time.time()) + 600),
        "payload": payload,
        "signature": {
            "type": "ed25519_signature",
            "public_key": "0x" + verify_key.encode().hex(),
            "signature": "0x"
        }
    }
    response = requests.post(f"{NODE_URL}/transactions", json=transaction, headers={"Content-Type": "application/json"})
    return response.json()

@app.get("/progress/{address}")
async def check_progress(address: str):
    try:
        if not address.startswith("0x"):
            address = "0x" + address
            
        if address not in students:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return students[address]
    except Exception as e:
        print(f"Error checking progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
