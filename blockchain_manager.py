import requests
import json
import os
from dotenv import load_dotenv
import time
import hashlib
import base64
import nacl.signing
import nacl.encoding

# Load environment variables
load_dotenv()

class BlockchainManager:
    def __init__(self):
        self.node_url = os.getenv("NODE_URL", "https://fullnode.devnet.aptoslabs.com")
        self.module_address = os.getenv("MODULE_ADDRESS", "CryptoLiteracy")
        self.module_name = os.getenv("MODULE_NAME", "LearningApp")
        self.private_key = os.getenv("PRIVATE_KEY", None)
        
        # In-memory storage for simulation mode
        self.students = {}
        self.lessons = {}
        self.completed_lessons = {}
    
    def connect_wallet(self, wallet_address):
        """Connect a wallet to the application"""
        # Validate wallet address format
        if not wallet_address.startswith("0x") or len(wallet_address) != 66:
            raise ValueError("Invalid wallet address format")
        
        # In a real implementation, we would verify the wallet exists
        # For simulation mode, we just return success
        return {
            "status": "success",
            "address": wallet_address,
            "mode": "simulation"
        }
    
    def register_student(self, student_address, private_key=None):
        """Register a new student"""
        # Validate wallet address format
        if not student_address.startswith("0x") or len(student_address) != 66:
            raise ValueError("Invalid wallet address format")
        
        # Check if student already exists
        if student_address in self.students:
            raise ValueError("Student already registered")
        
        # Register student in local storage
        self.students[student_address] = {
            "address": student_address,
            "registration_time": int(time.time()),
            "completed_lessons": []
        }
        
        # If private key is provided, register on blockchain
        if private_key:
            try:
                # In a real implementation, we would call the blockchain
                # For now, we just return a simulated transaction hash
                tx_hash = f"0x{hashlib.sha256(f'{student_address}{int(time.time())}'.encode()).hexdigest()}"
                return {
                    "status": "success",
                    "transaction_hash": tx_hash
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Return simulation result
        return {
            "status": "simulation",
            "message": "Student registered in simulation mode"
        }
    
    def create_lesson(self, lesson_id, title, description, reward_amount, private_key=None):
        """Create a new lesson"""
        # Store lesson in local storage
        self.lessons[lesson_id] = {
            "id": lesson_id,
            "title": title,
            "description": description,
            "reward_amount": reward_amount,
            "creation_time": int(time.time())
        }
        
        # If private key is provided, create on blockchain
        if private_key:
            try:
                # In a real implementation, we would call the blockchain
                # For now, we just return a simulated transaction hash
                tx_hash = f"0x{hashlib.sha256(f'{lesson_id}{title}{int(time.time())}'.encode()).hexdigest()}"
                return {
                    "status": "success",
                    "transaction_hash": tx_hash
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Return simulation result
        return {
            "status": "simulation",
            "message": "Lesson created in simulation mode"
        }
    
    def complete_lesson(self, student_address, sender_address, lesson_id, reward_amount, private_key=None):
        """Complete a lesson and send reward"""
        # Validate addresses
        if not student_address.startswith("0x") or len(student_address) != 66:
            raise ValueError("Invalid student wallet address format")
        if not sender_address.startswith("0x") or len(sender_address) != 66:
            raise ValueError("Invalid sender wallet address format")
        
        # Check if student exists
        if student_address not in self.students:
            raise ValueError("Student not found")
        
        # Check if lesson exists
        if lesson_id not in self.lessons:
            raise ValueError("Lesson not found")
        
        # Check if lesson is already completed
        if lesson_id in self.students[student_address]["completed_lessons"]:
            raise ValueError("Lesson already completed")
        
        # Update student record
        self.students[student_address]["completed_lessons"].append(lesson_id)
        
        # If private key is provided, execute real transaction
        if private_key:
            try:
                # In a real implementation, we would call the blockchain
                # For now, we just return a simulated transaction hash
                tx_hash = f"0x{hashlib.sha256(f'{student_address}{lesson_id}{int(time.time())}'.encode()).hexdigest()}"
                return {
                    "status": "success",
                    "transaction_hash": tx_hash,
                    "reward_amount": reward_amount
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Return simulation result
        return {
            "status": "simulation",
            "message": "Lesson completed in simulation mode",
            "reward_amount": reward_amount
        }
    
    def get_student_progress(self, student_address):
        """Get student progress"""
        # Validate wallet address format
        if not student_address.startswith("0x") or len(student_address) != 66:
            raise ValueError("Invalid wallet address format")
        
        # Check if student exists
        if student_address not in self.students:
            raise ValueError("Student not found")
        
        # Get student data
        student = self.students[student_address]
        
        # Calculate total rewards
        total_rewards = 0
        for lesson_id in student["completed_lessons"]:
            if lesson_id in self.lessons:
                total_rewards += self.lessons[lesson_id]["reward_amount"]
        
        # Return student progress
        return {
            "student_address": student_address,
            "lessons_completed": student["completed_lessons"],
            "total_rewards": total_rewards
        }
    
    def execute_transaction(self, from_address, to_address, amount, private_key=None):
        """Execute a direct token transfer"""
        # Validate addresses
        if not from_address.startswith("0x") or len(from_address) != 66:
            raise ValueError("Invalid sender wallet address format")
        if not to_address.startswith("0x") or len(to_address) != 66:
            raise ValueError("Invalid recipient wallet address format")
        
        # If private key is provided, execute real transaction
        if private_key:
            try:
                # In a real implementation, we would call the blockchain
                # For now, we just return a simulated transaction hash
                tx_hash = f"0x{hashlib.sha256(f'{from_address}{to_address}{amount}{int(time.time())}'.encode()).hexdigest()}"
                return {
                    "status": "success",
                    "transaction_hash": tx_hash
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Return simulation result
        return {
            "status": "simulation",
            "message": "Transaction executed in simulation mode"
        }

    def validate_private_key(self, address: str, private_key: str) -> bool:
        """Validate if a private key corresponds to a wallet address"""
        try:
            # Create signing key from private key
            signing_key = SigningKey(bytes.fromhex(private_key.replace("0x", "")))
            
            # Get public key
            public_key = signing_key.verify_key.encode(encoder=HexEncoder).decode()
            
            # Derive address from public key
            derived_address = "0x" + hashlib.sha3_256(bytes.fromhex(public_key)).hexdigest()
            
            # Check if the address matches
            return derived_address == address
        except Exception as e:
            print(f"Error validating private key: {str(e)}")
            return False
    
    def _execute_transaction(self, payload: dict, private_key: str) -> str:
        """Execute a transaction on the blockchain"""
        try:
            # Create signing key from private key
            signing_key = SigningKey(bytes.fromhex(private_key.replace("0x", "")))
            
            # Sign the transaction payload
            signature = signing_key.sign(json.dumps(payload).encode())
            signature_hex = base64.b64encode(signature).decode()
            
            # Prepare transaction request
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Add signature to payload
            payload["signature"] = signature_hex
            
            # Submit transaction
            response = requests.post(
                f"{self.node_url}/v1/transactions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 202:
                raise Exception(f"Transaction submission failed: {response.text}")
            
            # Get transaction hash
            txn_hash = response.json().get("hash")
            
            # Wait for transaction to be confirmed
            self._wait_for_transaction(txn_hash)
            
            return txn_hash
        except Exception as e:
            print(f"Error executing transaction: {str(e)}")
            raise
    
    def _wait_for_transaction(self, txn_hash: str, max_retries: int = 10, delay: int = 1):
        """Wait for a transaction to be confirmed"""
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.node_url}/v1/transactions/{txn_hash}")
                if response.status_code == 200:
                    txn_data = response.json()
                    if txn_data.get("success", False):
                        return True
                time.sleep(delay)
            except Exception:
                time.sleep(delay)
        
        raise Exception("Transaction confirmation timeout") 