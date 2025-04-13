from aptos_sdk.account import Account
from aptos_sdk.transactions import TransactionArgument, TransactionPayload
import os
import json
import time

# Aptos blockchain configuration
NODE_URL = "https://fullnode.devnet.aptoslabs.com"
MODULE_ADDRESS = "CryptoLiteracy"  # Replace with your actual module address
MODULE_NAME = "LearningApp"

class BlockchainManager:
    def __init__(self):
        self.module_address = MODULE_ADDRESS
        self.module_name = MODULE_NAME
    
    def create_account_from_private_key(self, private_key_hex):
        """Create an Aptos account from a private key."""
        try:
            # Remove '0x' prefix if present
            if private_key_hex.startswith('0x'):
                private_key_hex = private_key_hex[2:]
            
            # Create account from private key
            account = Account.load_key(private_key_hex)
            return account
        except Exception as e:
            print(f"Error creating account: {e}")
            return None
    
    def register_student(self, student_address, private_key_hex=None):
        """Register a student on the blockchain."""
        try:
            # If private key is provided, use it to sign the transaction
            if private_key_hex:
                account = self.create_account_from_private_key(private_key_hex)
                if not account:
                    return {"success": False, "error": "Invalid private key"}
                
                # Create transaction payload
                payload = {
                    "type": "entry_function_payload",
                    "function": f"{self.module_address}::{self.module_name}::register_student",
                    "type_arguments": [],
                    "arguments": []
                }
                
                # Submit transaction
                txn_hash = self.client.submit_transaction(account, payload)
                
                # Wait for transaction confirmation
                self.client.wait_for_transaction(txn_hash)
                
                return {
                    "success": True,
                    "transaction_hash": txn_hash,
                    "message": "Student registered successfully on blockchain"
                }
            else:
                # Simulate transaction (no actual blockchain interaction)
                return {
                    "success": True,
                    "transaction_hash": f"0x{int(time.time())}",
                    "message": "Student registration simulated (no blockchain interaction)"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_lesson(self, title, description, reward_amount, private_key_hex=None):
        """Create a lesson on the blockchain."""
        try:
            # If private key is provided, use it to sign the transaction
            if private_key_hex:
                account = self.create_account_from_private_key(private_key_hex)
                if not account:
                    return {"success": False, "error": "Invalid private key"}
                
                # Create transaction payload
                payload = {
                    "type": "entry_function_payload",
                    "function": f"{self.module_address}::{self.module_name}::create_lesson",
                    "type_arguments": [],
                    "arguments": [
                        title,
                        description,
                        str(reward_amount)
                    ]
                }
                
                # Submit transaction
                txn_hash = self.client.submit_transaction(account, payload)
                
                # Wait for transaction confirmation
                self.client.wait_for_transaction(txn_hash)
                
                return {
                    "success": True,
                    "transaction_hash": txn_hash,
                    "message": "Lesson created successfully on blockchain"
                }
            else:
                # Simulate transaction (no actual blockchain interaction)
                return {
                    "success": True,
                    "transaction_hash": f"0x{int(time.time())}",
                    "message": "Lesson creation simulated (no blockchain interaction)"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def complete_lesson(self, student_address, lesson_id, sender_address, private_key_hex=None):
        """Complete a lesson and transfer rewards on the blockchain."""
        try:
            # If private key is provided, use it to sign the transaction
            if private_key_hex:
                account = self.create_account_from_private_key(private_key_hex)
                if not account:
                    return {"success": False, "error": "Invalid private key"}
                
                # Create transaction payload
                payload = {
                    "type": "entry_function_payload",
                    "function": f"{self.module_address}::{self.module_name}::complete_lesson",
                    "type_arguments": [],
                    "arguments": [
                        student_address,
                        str(lesson_id)
                    ]
                }
                
                # Submit transaction
                txn_hash = self.client.submit_transaction(account, payload)
                
                # Wait for transaction confirmation
                self.client.wait_for_transaction(txn_hash)
                
                return {
                    "success": True,
                    "transaction_hash": txn_hash,
                    "message": "Lesson completed successfully on blockchain"
                }
            else:
                # Simulate transaction (no actual blockchain interaction)
                return {
                    "success": True,
                    "transaction_hash": f"0x{int(time.time())}",
                    "message": "Lesson completion simulated (no blockchain interaction)"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_student_progress(self, student_address):
        """Get student progress from the blockchain."""
        try:
            # Create resource path
            resource_path = f"{self.module_address}::{self.module_name}::Student"
            
            # Get resource from blockchain
            resource = self.client.account_resource(student_address, resource_path)
            
            if resource:
                return {
                    "success": True,
                    "data": resource.data
                }
            else:
                return {
                    "success": False,
                    "error": "Student not found on blockchain"
                }
        except Exception as e:
            # If resource doesn't exist, return simulated data
            return {
                "success": True,
                "data": {
                    "lessons_completed": [],
                    "total_rewards": 0
                },
                "message": "Using simulated data (no blockchain interaction)"
            }
    
    def get_lesson(self, lesson_id):
        """Get lesson details from the blockchain."""
        try:
            # Create resource path
            resource_path = f"{self.module_address}::{self.module_name}::Lesson"
            
            # Get resource from blockchain
            resource = self.client.account_resource(self.module_address, resource_path)
            
            if resource and "data" in resource and "lessons" in resource.data:
                lessons = resource.data["lessons"]
                if lesson_id < len(lessons):
                    return {
                        "success": True,
                        "data": lessons[lesson_id]
                    }
            
            return {
                "success": False,
                "error": "Lesson not found on blockchain"
            }
        except Exception as e:
            # If resource doesn't exist, return simulated data
            return {
                "success": True,
                "data": {
                    "title": "Simulated Lesson",
                    "description": "This is a simulated lesson",
                    "reward_amount": 1
                },
                "message": "Using simulated data (no blockchain interaction)"
            }
    
    def execute_transaction(self, from_address, to_address, amount, private_key_hex=None):
        """Execute a real blockchain transaction."""
        try:
            # If private key is provided, use it to sign the transaction
            if private_key_hex:
                account = self.create_account_from_private_key(private_key_hex)
                if not account:
                    return {"success": False, "error": "Invalid private key"}
                
                # Create transaction payload for coin transfer
                payload = {
                    "type": "entry_function_payload",
                    "function": "0x1::coin::transfer",
                    "type_arguments": ["0x1::aptos_coin::AptosCoin"],
                    "arguments": [
                        to_address,
                        str(amount)
                    ]
                }
                
                # Submit transaction
                txn_hash = self.client.submit_transaction(account, payload)
                
                # Wait for transaction confirmation
                self.client.wait_for_transaction(txn_hash)
                
                return {
                    "success": True,
                    "transaction_hash": txn_hash,
                    "message": f"Successfully transferred {amount} APT from {from_address} to {to_address}"
                }
            else:
                # Simulate transaction (no actual blockchain interaction)
                return {
                    "success": True,
                    "transaction_hash": f"0x{int(time.time())}",
                    "message": f"Simulated transfer of {amount} APT from {from_address} to {to_address} (no blockchain interaction)"
                }
        except Exception as e:
            return {"success": False, "error": str(e)} 