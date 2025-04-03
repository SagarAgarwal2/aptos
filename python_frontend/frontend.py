import streamlit as st
import requests

# Backend API URL
API_URL = "http://127.0.0.1:8000"

# Set page config for a cleaner look
st.set_page_config(
    page_title="Crypto Literacy Learning App",
    page_icon="📚",
    layout="wide"
)

# Custom CSS to hide technical messages
st.markdown("""
<style>
    .stAlert {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .stInfo {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    .stMarkdown {
        font-size: 16px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

st.title("Crypto Literacy Learning App")

# Navigation
menu = st.sidebar.selectbox("Menu", ["Register Student", "Create Lesson", "Complete Lesson", "Check Progress"])

# Register Student
if menu == "Register Student":
    st.subheader("Register a new student")
    student_address = st.text_input("Enter Student Wallet Address")
    
    if st.button("Register"):
        try:
            response = requests.post(f"{API_URL}/register", json={"student_address": student_address})
            if response.status_code == 200:
                st.success("Student registered successfully!")
            else:
                st.error("Student already registered. Please try a different address.")
        except:
            st.error("Could not connect to the server. Please try again later.")

# Create Lesson
elif menu == "Create Lesson":
    st.subheader("Create a new lesson")
    title = st.text_input("Lesson Title")
    description = st.text_area("Lesson Description")
    reward_amount = st.number_input("Reward Amount (APT)", min_value=0, step=1)

    if st.button("Create Lesson"):
        try:
            response = requests.post(f"{API_URL}/create_lesson", json={"title": title, "description": description, "reward_amount": reward_amount})
            if response.status_code == 200:
                lesson_id = response.json()["lesson_id"]
                st.success(f"Lesson created successfully! Your lesson ID is: {lesson_id}")
            else:
                st.error("Failed to create lesson. Please try again.")
        except:
            st.error("Could not connect to the server. Please try again later.")

# Complete Lesson
elif menu == "Complete Lesson":
    st.subheader("Complete a lesson")
    
    # Display available lessons
    try:
        lessons_response = requests.get(f"{API_URL}/lessons")
        if lessons_response.status_code == 200:
            lessons = lessons_response.json()
            if lessons:
                st.write("Available Lessons:")
                for lesson in lessons:
                    st.markdown(f"**Lesson {lesson['id']}**: {lesson['title']} - Reward: {lesson['reward_amount']} APT")
            else:
                st.info("No lessons available yet. Please create some lessons first.")
    except:
        st.error("Could not fetch lessons. Please make sure the backend server is running.")
    
    student_address = st.text_input("Enter Student Wallet Address")
    lesson_id = st.number_input("Enter Lesson ID", min_value=0, step=1)

    if st.button("Complete Lesson"):
        try:
            response = requests.post(f"{API_URL}/complete_lesson", json={"student_address": student_address, "lesson_id": lesson_id})
            if response.status_code == 200:
                st.success("Lesson completed successfully!")
            elif response.status_code == 404:
                st.error("Student or lesson not found. Please check your inputs.")
            elif response.status_code == 400:
                st.error("You have already completed this lesson.")
            else:
                st.error("Failed to complete lesson. Please try again.")
        except:
            st.error("Could not connect to the server. Please try again later.")

# Check Progress
elif menu == "Check Progress":
    st.subheader("Check Student Progress")
    student_address = st.text_input("Enter Student Wallet Address")

    if st.button("Get Progress"):
        try:
            response = requests.get(f"{API_URL}/progress/{student_address}")
            if response.status_code == 200:
                data = response.json()
                
                # Create a clean progress display
                st.markdown("### Your Progress")
                
                if data["lessons_completed"]:
                    st.markdown(f"**Lessons Completed:** {len(data['lessons_completed'])}")
                    st.markdown(f"**Total Rewards Earned:** {data['total_rewards']} APT")
                    
                    # Show completed lesson details
                    try:
                        lessons_response = requests.get(f"{API_URL}/lessons")
                        if lessons_response.status_code == 200:
                            lessons = {lesson["id"]: lesson for lesson in lessons_response.json()}
                            st.markdown("#### Completed Lessons:")
                            for lesson_id in data["lessons_completed"]:
                                if lesson_id in lessons:
                                    lesson = lessons[lesson_id]
                                    st.markdown(f"- **{lesson['title']}** (Reward: {lesson['reward_amount']} APT)")
                    except:
                        pass
                else:
                    st.info("You haven't completed any lessons yet. Start learning to earn rewards!")
            else:
                st.error("Student not found. Please check your address.")
        except:
            st.error("Could not connect to the server. Please try again later.")
