import streamlit as st
import google.generativeai as genai
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Industria Status", page_icon="🏭", layout="wide")

st.title("🏭 Industria: Autonomous Maintenance Agent")
st.markdown("### Enterprise AI for Industrial Automation")

# --- SIDEBAR: SETUP ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.markdown("[Get your API Key here](https://aistudio.google.com/app/apikey)")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("API Key Configured")
        except Exception as e:
            st.error(f"Error configuring API: {e}")

# --- THE TOOLS (Backend) ---
def get_machine_telemetry(machine_id: str):
    """Retrieves real-time sensor data."""
    # Simulation logic for the demo
    if machine_id == "CNC-01":
        return {"status": "running", "temperature_c": 105, "vibration_level": "critical", "alert": "OVERHEATING"}
    elif machine_id == "Pump-A":
        return {"status": "idle", "temperature_c": 45, "vibration_level": "normal"}
    else:
        return {"error": "Machine ID not found. Try 'CNC-01' or 'Pump-A'."}

def log_maintenance_ticket(machine_id: str, priority: str, issue: str, action: str):
    """Logs a ticket."""
    return f"✅ TICKET LOGGED: [{machine_id}] Priority: {priority} | Action: {action}"

tools_list = [get_machine_telemetry, log_maintenance_ticket]

# --- SYSTEM INSTRUCTION ---
system_instruction = """
You are Industria, an expert site reliability engineer.
MANUAL:
1. Normal: Temp < 80C.
2. Warning: Temp 80-90C -> Log MEDIUM ticket.
3. CRITICAL: Temp > 100C -> Log HIGH ticket + EMERGENCY STOP.

INSTRUCTIONS:
- Always check telemetry first using the tool.
- Explain your reasoning based on the manual.
- If Critical, you MUST log a ticket.
"""

# --- CHAT INTERFACE ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Site Engineer Chat")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input Area
    if prompt := st.chat_input("Ex: 'Check status of CNC-01'"):
        if not api_key:
            st.error("Please enter your API Key in the sidebar first!")
        else:
            # User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Agent Response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("🔄 *Accessing SCADA systems...*")
                
                try:
                    # Initialize Model (Gemini 2.0 Flash)
                    model = genai.GenerativeModel(
                        model_name='models/gemini-2.0-flash', 
                        tools=tools_list,
                        system_instruction=system_instruction
                    )
                    chat = model.start_chat(enable_automatic_function_calling=True)
                    
                    response = chat.send_message(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    message_placeholder.error(f"Connection Error: {e}")

with col2:
    st.subheader("📡 Live Telemetry View")
    st.info("System Status: ONLINE")
    st.metric(label="Pump-A Temp", value="45°C", delta="-2°C")
    st.metric(label="CNC-01 Temp", value="105°C", delta="CRITICAL", delta_color="inverse")
    st.write("---")
    st.caption("Monitoring Agent v1.0")