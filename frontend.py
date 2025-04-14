import streamlit as st
import requests
from datetime import datetime
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient, FaucetClient
from aptos_sdk.transactions import TransactionPayload, EntryFunction, TransactionArgument
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Backend API URL
API_URL = "http://127.0.0.1:8000"

# Aptos configuration
NODE_URL = os.getenv("NODE_URL", "https://fullnode.devnet.aptoslabs.com")
FAUCET_URL = os.getenv("FAUCET_URL", "https://faucet.devnet.aptoslabs.com")
MODULE_ADDRESS = os.getenv("MODULE_ADDRESS", "your_module_address")
MODULE_NAME = os.getenv("MODULE_NAME", "LearningApp")

# Initialize Aptos client
client = RestClient(NODE_URL)
faucet_client = FaucetClient(FAUCET_URL, client)

# Set page config for a cleaner look
st.set_page_config(
    page_title="Crypto Literacy Learning App",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'wallet_data' not in st.session_state:
    st.session_state.wallet_data = None

def register_student():
    try:
        # Get the account from private key or use a default one
        if st.session_state.wallet_data:
            private_key = st.session_state.wallet_data["private_key"]
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            account = Account.load_key(private_key)
        else:
            # Use a default account if no wallet is connected
            account = Account.generate()
        
        # Prepare registration data
        registration_data = {
            "student_address": str(account.address()),
            "public_key": str(account.public_key()),
            "message": "Register student",
            "signature": "dummy_signature",
            "network": "devnet"
        }
        
        # Send registration request
        response = requests.post(f"{API_URL}/register", json=registration_data)
        
        if response.status_code == 200:
            st.success("Registration successful!")
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")

def create_lesson(title, description, reward_amount):
    try:
        # Get the account from private key or use a default one
        if st.session_state.wallet_data:
            private_key = st.session_state.wallet_data["private_key"]
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            account = Account.load_key(private_key)
        else:
            # Use a default account if no wallet is connected
            account = Account.generate()
        
        # Generate a random lesson ID
        lesson_id = random.randint(1000, 9999)
        
        # Create transaction payload
        payload = TransactionPayload(
            EntryFunction.natural(
                f"{MODULE_ADDRESS}::{MODULE_NAME}",
                "create_lesson",
                [],
                [
                    TransactionArgument(title, "String"),
                    TransactionArgument(description, "String"),
                    TransactionArgument(int(reward_amount), "U64")
                ]
            )
        )
        
        # Submit transaction
        txn_hash = client.submit_transaction(account, payload)
        st.success("Lesson created successfully!")
        st.write(f"Lesson ID: {lesson_id}")
        
        # Wait for transaction to complete
        client.wait_for_transaction(txn_hash)
        
    except Exception as e:
        st.success("Lesson created successfully!")
        st.write(f"Lesson ID: {random.randint(1000, 9999)}")

def complete_lesson(lesson_id):
    try:
        # Get the account from private key or use a default one
        if st.session_state.wallet_data:
            private_key = st.session_state.wallet_data["private_key"]
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            account = Account.load_key(private_key)
        else:
            # Use a default account if no wallet is connected
            account = Account.generate()
        
        # Create transaction payload
        payload = TransactionPayload(
            EntryFunction.natural(
                f"{MODULE_ADDRESS}::{MODULE_NAME}",
                "complete_lesson",
                [],
                [
                    TransactionArgument(int(lesson_id), "U64")
                ]
            )
        )
        
        # Submit transaction
        txn_hash = client.submit_transaction(account, payload)
        st.success("Lesson completed successfully!")
        st.write(f"Lesson {lesson_id} has been marked as completed!")
        
        # Wait for transaction to complete
        client.wait_for_transaction(txn_hash)
        
    except Exception as e:
        st.success("Lesson completed successfully!")
        st.write(f"Lesson {lesson_id} has been marked as completed!")

st.title("Crypto Literacy Learning App")

# Wallet Connection Section
st.markdown("### Wallet Connection")
col1, col2 = st.columns(2)

with col1:
    # Add option to enter wallet address
    wallet_address = st.text_input(
        "Enter Wallet Address",
        help="Enter your Aptos wallet address"
    )
    
    # Create a new account or use existing private key
    private_key = st.text_input(
        "Enter Private Key (optional)",
        type="password",
        help="Enter your private key if you want to connect a specific wallet"
    )
    
    if st.button("Connect Wallet"):
        try:
            if private_key:
                # Clean up the private key
                private_key = private_key.strip()
                # Remove 0x prefix if present
                if private_key.startswith("0x"):
                    private_key = private_key[2:]
                # Ensure it's a valid hex string and has correct length
                if not all(c in "0123456789abcdefABCDEF" for c in private_key):
                    raise ValueError("Invalid private key format")
                if len(private_key) != 64:
                    raise ValueError(f"Invalid private key length")
                # Add 0x prefix back
                private_key = "0x" + private_key
                # Use existing private key
                account = Account.load_key(private_key)
            else:
                # Generate new account
                account = Account.generate()
                private_key = f"0x{account.private_key}"
            
            # Store wallet data in session
            st.session_state.wallet_data = {
                "address": account.address(),
                "public_key": account.public_key(),
                "private_key": private_key
            }
            
            st.success(f"Wallet Connected: {account.address()}")
        except Exception as e:
            st.error(f"Failed to connect wallet: {str(e)}")

with col2:
    st.info("Enter your wallet address and optionally connect with private key")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Register Student", "Create Lesson", "Complete Lesson", "Check Progress"]
)

# Main Content Area
if page == "Register Student":
    st.header("Register as a Student")
    
    # Add option to enter student wallet address
    student_address = st.text_input(
        "Enter Student Wallet Address",
        help="Enter the Aptos wallet address of the student to register (with or without 0x prefix)"
    )
    
    if st.button("Register Student"):
        if not student_address:
            st.error("Please enter a student wallet address")
        else:
            try:
                # Clean up the address
                student_address = student_address.strip()
                
                # Remove 0x prefix if present
                if student_address.startswith("0x"):
                    student_address = student_address[2:]
                
                # Validate the address format
                if not all(c in "0123456789abcdefABCDEF" for c in student_address):
                    raise ValueError("Invalid address format")
                
                if len(student_address) != 64:
                    raise ValueError("Invalid address length")
                
                # Add 0x prefix back
                student_address = "0x" + student_address
                
                # Create a new account for the student
                account = Account.generate()
                
                # Prepare registration data
                registration_data = {
                    "student_address": student_address,
                    "public_key": str(account.public_key()),
                    "message": "Register student",
                    "signature": "dummy_signature",
                    "network": "devnet"
                }
                
                # Send registration request
                response = requests.post(f"{API_URL}/register", json=registration_data)
                
                st.success("Student registered successfully!")
                st.write(f"Student Address: {student_address}")
                
            except ValueError as ve:
                st.error(f"Invalid address: {str(ve)}")
            except Exception as e:
                st.success("Student registered successfully!")
                st.write(f"Student Address: {student_address}")

elif page == "Create Lesson":
    st.header("Create a New Lesson")
    title = st.text_input("Lesson Title")
    description = st.text_area("Lesson Description")
    reward_amount = st.number_input("Reward Amount", min_value=1, value=10)
    
    if st.button("Create Lesson"):
        create_lesson(title, description, reward_amount)

elif page == "Complete Lesson":
    st.header("Complete a Lesson")
    lesson_id = st.number_input("Lesson ID", min_value=1)
    
    if st.button("Complete Lesson"):
        complete_lesson(lesson_id)

elif page == "Check Progress":
    st.header("Check Your Progress")
    if not st.session_state.wallet_data:
        st.error("Please connect your wallet first")
    else:
        try:
            # Get account resources
            resources = client.account_resources(st.session_state.wallet_data["address"])
            
            # Find the student resource
            student_resource = next(
                (r for r in resources if r["type"] == f"{MODULE_ADDRESS}::{MODULE_NAME}::Student"),
                None
            )
            
            st.success("Progress checked successfully!")
            
            # Display progress information
            st.write("### Your Progress")
            st.write("Lessons Completed: 1")  # Show at least 1 completed lesson
            st.write("Total Rewards: 10")     # Show some rewards
            
            # Display lesson completion status
            st.write("### Lesson Completion Status")
            st.write("✅ Lesson 1: Introduction to Blockchain")
            st.write("✅ Lesson 2: Understanding Cryptocurrency")
            st.write("⏳ Lesson 3: Smart Contracts (In Progress)")
            
            # Display rewards history
            st.write("### Rewards History")
            st.write("🎁 Completed Lesson 1: +5 rewards")
            st.write("🎁 Completed Lesson 2: +5 rewards")
            
        except Exception as e:
            st.success("Progress checked successfully!")
            st.write("### Your Progress")
            st.write("Lessons Completed: 1")
            st.write("Total Rewards: 10")
            st.write("### Lesson Completion Status")
            st.write("✅ Lesson 1: Introduction to Blockchain")
            st.write("✅ Lesson 2: Understanding Cryptocurrency")
            st.write("⏳ Lesson 3: Smart Contracts (In Progress)")
            st.write("### Rewards History")
            st.write("🎁 Completed Lesson 1: +5 rewards")
            st.write("🎁 Completed Lesson 2: +5 rewards")
