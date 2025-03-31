import streamlit as st
import requests

# Backend API URL (Make sure FastAPI is running on this address)
BACKEND_URL = "http://127.0.0.1:8000"

# Streamlit UI
st.title("📚 Crypto Literacy Learning App")
st.subheader("Powered by Aptos Blockchain")

# Register a new student
st.header("👤 Register a Student")
student_address = st.text_input("Enter Student Wallet Address")
if st.button("Register"):
    response = requests.post(f"{BACKEND_URL}/register", json={"student_address": student_address})
    if response.status_code == 200:
        st.success("✅ Student Registered Successfully!")
    else:
        st.error("❌ Registration Failed. Try Again!")

# Reward a student
st.header("🎁 Reward a Student")
reward_address = st.text_input("Enter Student Wallet Address for Reward")
reward_amount = st.number_input("Enter Reward Amount (APT)", min_value=1, step=1)
if st.button("Reward"):
    response = requests.post(f"{BACKEND_URL}/reward", json={"student_address": reward_address, "amount": reward_amount})
    if response.status_code == 200:
        st.success(f"✅ {reward_amount} APT Sent Successfully!")
    else:
        st.error("❌ Reward Transaction Failed!")

# Check student progress
st.header("📊 Check Student Progress")
check_address = st.text_input("Enter Student Wallet Address to Check Progress")
if st.button("Check Progress"):
    response = requests.get(f"{BACKEND_URL}/progress/{check_address}")
    if response.status_code == 200:
        data = response.json()
        st.write(f"📚 Lessons Completed: **{data['lessons_completed']}**")
        st.write(f"💰 Total Rewards Earned: **{data['total_rewards']} APT**")
    else:
        st.error("❌ Could not fetch student progress.")

st.markdown("---")
st.caption("🔗 Connected to Aptos Blockchain via FastAPI & Python SDK")
