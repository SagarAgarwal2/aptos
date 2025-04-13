import streamlit as st
import requests
from datetime import datetime

# Backend API URL
API_URL = "http://127.0.0.1:8000"

# Set page config for a cleaner look
st.set_page_config(
    page_title="Crypto Literacy Learning App",
    page_icon="📚",
    layout="wide"
)

# Add Petra Wallet JavaScript
st.markdown("""
<script>
    let petra = null;
    
    async function connectWallet() {
        try {
            if (typeof window.aptos === 'undefined') {
                alert('Please install Petra Wallet first!');
                window.open('https://petra.app/', '_blank');
                return;
            }
            
            petra = window.aptos;
            const account = await petra.connect();
            
            // Sign a test message
            const message = "Welcome to Crypto Literacy Learning App";
            const signature = await petra.signMessage({
                message: message,
                nonce: Date.now().toString()
            });
            
            // Store wallet info in session state
            window.parent.postMessage({
                type: 'petra_connected',
                address: account.address,
                network: account.network,
                publicKey: account.publicKey,
                signature: signature.signature,
                message: message
            }, '*');
            
            document.getElementById('wallet-status').innerText = `Connected: ${account.address}`;
            document.getElementById('connect-button').style.display = 'none';
            document.getElementById('disconnect-button').style.display = 'block';
        } catch (error) {
            console.error('Failed to connect:', error);
            alert('Failed to connect to wallet: ' + error.message);
        }
    }

    async function disconnectWallet() {
        try {
            if (petra) {
                await petra.disconnect();
                window.parent.postMessage({
                    type: 'petra_disconnected'
                }, '*');
                document.getElementById('wallet-status').innerText = 'Not Connected';
                document.getElementById('connect-button').style.display = 'block';
                document.getElementById('disconnect-button').style.display = 'none';
            }
        } catch (error) {
            console.error('Failed to disconnect:', error);
        }
    }
</script>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .wallet-container {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .wallet-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        margin-right: 10px;
    }
    .wallet-button:hover {
        background-color: #45a049;
    }
    .wallet-status {
        color: #666;
        font-size: 14px;
        margin-top: 10px;
    }
    .error-message {
        color: red;
        font-size: 14px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'petra_connected' not in st.session_state:
    st.session_state.petra_connected = False
    st.session_state.petra_address = None
    st.session_state.petra_network = None
    st.session_state.petra_public_key = None
    st.session_state.petra_signature = None
    st.session_state.petra_message = None

st.title("Crypto Literacy Learning App")

# Wallet Connection Section
st.markdown("### Wallet Connection")
col1, col2 = st.columns(2)
with col1:
    if not st.session_state.petra_connected:
        if st.button("Connect Petra Wallet", key="connect-button"):
            st.markdown("""
            <script>
                connectWallet();
            </script>
            """, unsafe_allow_html=True)
            st.markdown('<div id="wallet-status" class="wallet-status">Connecting...</div>', unsafe_allow_html=True)
    else:
        st.success(f"Wallet Connected: {st.session_state.petra_address}")
        if st.button("Disconnect Wallet", key="disconnect-button"):
            st.markdown("""
            <script>
                disconnectWallet();
            </script>
            """, unsafe_allow_html=True)
            st.session_state.petra_connected = False
            st.session_state.petra_address = None
            st.session_state.petra_network = None
            st.session_state.petra_public_key = None
            st.session_state.petra_signature = None
            st.session_state.petra_message = None
            st.experimental_rerun()

with col2:
    st.info("Connect your Petra Wallet to perform transactions")

# Navigation
menu = st.sidebar.selectbox("Menu", ["Register Student", "Create Lesson", "Complete Lesson", "Check Progress"])

# Register Student
if menu == "Register Student":
    st.subheader("Register a new student")
    student_address = st.text_input("Enter Student Wallet Address")
    
    if st.button("Register"):
        try:
            if not student_address:
                st.error("Please enter a student address to register")
            else:
                # Prepare registration data with proper formatting
                registration_data = {
                    "student_address": student_address.strip(),
                    "public_key": student_address.strip(),
                    "message": f"Register student {student_address.strip()}",
                    "signature": "dummy_signature",
                    "network": "devnet"
                }
                
                # Make sure the backend is running
                try:
                    # First check if the backend is accessible
                    health_check = requests.get(f"{API_URL}/")
                    if health_check.status_code != 200:
                        st.error("Backend server is not responding. Please make sure it's running.")
                    else:
                        # Send registration request
                        response = requests.post(
                            f"{API_URL}/register",
                            json=registration_data,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if response.status_code == 200:
                            st.success("Student registered successfully!")
                        else:
                            try:
                                error_detail = response.json().get('detail', 'Unknown error')
                                st.error(f"Registration failed: {error_detail}")
                            except:
                                st.error(f"Registration failed: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend server. Please make sure it's running.")
        except Exception as e:
            st.error(f"Could not connect to the server: {str(e)}")

# Create Lesson
elif menu == "Create Lesson":
    st.subheader("Create a new lesson")
    title = st.text_input("Lesson Title")
    description = st.text_area("Lesson Description")
    reward_amount = st.number_input("Reward Amount", min_value=1, value=10)
    
    if st.button("Create Lesson"):
        try:
            if not title or not description:
                st.error("Please fill in all required fields")
            else:
                lesson_data = {
                    "title": title,
                    "description": description,
                    "reward_amount": reward_amount,
                    "public_key": st.session_state.petra_public_key if st.session_state.petra_connected else "dummy_public_key",
                    "message": f"Create lesson: {title}",
                    "signature": st.session_state.petra_signature if st.session_state.petra_connected else "dummy_signature",
                    "network": st.session_state.petra_network if st.session_state.petra_connected else "devnet"
                }
                
                response = requests.post(f"{API_URL}/create_lesson", json=lesson_data)
                if response.status_code == 200:
                    result = response.json()
                    lesson_id = result.get('lesson_id')
                    st.success(f"Lesson created successfully! Lesson ID: {lesson_id}")
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"Lesson creation failed: {error_detail}")
        except Exception as e:
            st.error(f"Could not connect to the server: {str(e)}")

# Complete Lesson
elif menu == "Complete Lesson":
    st.subheader("Complete a lesson")
    student_address = st.text_input("Enter Student Wallet Address", 
                                  value=st.session_state.petra_address if st.session_state.petra_connected else "")
    lesson_id = st.number_input("Enter Lesson ID", min_value=0, step=1)
    
    if st.button("Complete Lesson"):
        try:
            if not student_address:
                st.error("Please enter a student address")
            elif not lesson_id:
                st.error("Please enter a lesson ID")
            else:
                completion_data = {
                    "student_address": student_address,
                    "lesson_id": lesson_id,
                    "public_key": st.session_state.petra_public_key if st.session_state.petra_connected else student_address,
                    "message": f"Complete lesson {lesson_id}",
                    "signature": st.session_state.petra_signature if st.session_state.petra_connected else "dummy_signature",
                    "network": st.session_state.petra_network if st.session_state.petra_connected else "devnet"
                }
                
                response = requests.post(f"{API_URL}/complete_lesson", json=completion_data)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Lesson completed successfully! Transaction Hash: {result.get('transaction_hash')}")
                    st.info(f"Reward Earned: {result.get('reward_earned')}")
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"Lesson completion failed: {error_detail}")
        except Exception as e:
            st.error(f"Could not connect to the server: {str(e)}")

# Check Progress
elif menu == "Check Progress":
    st.subheader("Check student progress")
    student_address = st.text_input("Enter Student Wallet Address", 
                                  value=st.session_state.petra_address if st.session_state.petra_connected else "")
    
    if st.button("Get Progress"):
        try:
            if not student_address:
                st.error("Please enter a student address")
            else:
                response = requests.get(f"{API_URL}/progress/{student_address}")
                if response.status_code == 200:
                    data = response.json()
                    st.write("### Student Progress")
                    st.write(f"Total Lessons Completed: {len(data['lessons_completed'])}")
                    st.write(f"Total Rewards Earned: {data['total_rewards']}")
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"Failed to get progress: {error_detail}")
        except Exception as e:
            st.error(f"Could not connect to the server: {str(e)}")

# Listen for wallet connection events
st.markdown("""
<script>
    window.addEventListener('message', (event) => {
        if (event.data.type === 'petra_connected') {
            window.parent.postMessage({
                type: 'update_session',
                data: {
                    petra_connected: true,
                    petra_address: event.data.address,
                    petra_network: event.data.network,
                    petra_public_key: event.data.publicKey,
                    petra_signature: event.data.signature,
                    petra_message: event.data.message
                }
            }, '*');
        }
    });
</script>
""", unsafe_allow_html=True)