import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Industria | Enterprise Maintenance", page_icon="🏭", layout="wide")

# Custom CSS to remove Streamlit padding and make it look like a web-app
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .stAlert {margin-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8637/8637099.png", width=50)
    st.title("Industria Control")
    st.caption("v2.1 Enterprise Edition")
    
    st.divider()
    
    api_key = st.text_input("🔑 Google API Key", type="password", help="Get this from Google AI Studio")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.success("System Connected")
        except:
            st.error("Invalid Key")
    else:
        st.warning("Please enter API Key")
        
    st.divider()
    st.markdown("### 🛠 System Status")
    st.success("🟢 Cloud Connection: Active")
    st.success("🟢 SCADA Bridge: Active")
    st.info("🔵 Agent: Idle")

# --- 3. MOCK DATA & TOOLS ---
def get_machine_telemetry(machine_id: str):
    """Retrieves real-time sensor data."""
    if machine_id == "CNC-01":
        return {"status": "running", "temperature_c": 105, "vibration_level": "critical", "alert": "OVERHEATING"}
    elif machine_id == "Pump-A":
        return {"status": "idle", "temperature_c": 45, "vibration_level": "normal"}
    else:
        return {"error": "Machine ID not found. Try 'CNC-01'."}

def log_maintenance_ticket(machine_id: str, priority: str, issue: str, action: str):
    return f"✅ TICKET LOGGED: [{machine_id}] Priority: {priority} | Action: {action}"

tools_list = [get_machine_telemetry, log_maintenance_ticket]

system_instruction = """
You are Industria, an expert site reliability engineer.
MANUAL:
1. Normal: Temp < 80C.
2. Warning: Temp 80-90C -> Log MEDIUM ticket.
3. CRITICAL: Temp > 100C -> Log HIGH ticket + EMERGENCY STOP.

INSTRUCTIONS:
- Always check telemetry first using the tool.
- If Critical, you MUST log a ticket.
- Be concise.
"""

# --- 4. MAIN DASHBOARD UI ---
st.title("🏭 Industria: Predictive Maintenance Console")
st.markdown("### 🤖 Autonomous Agent for Industrial IoT")

# TOP METRICS ROW
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Machines", "12", "Running")
col2.metric("Plant Efficiency", "94.2%", "+1.2%")
col3.metric("Energy Usage", "450 kW", "-5%")
col4.metric("Safety Incidents", "0", "Last 24h")

st.divider()

# MAIN CONTENT AREA (2 Columns: Chat vs Data)
left_col, right_col = st.columns([1.5, 1])

with left_col:
    st.subheader("💬 Site Engineer Interface")
    
    # Chat Container
    chat_container = st.container(height=400)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👷‍♂️"):
                st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ex: 'Check status of CNC-01'"):
        if not api_key:
            st.error("Please configure API Key in Sidebar")
        else:
            # User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="👷‍♂️"):
                    st.markdown(prompt)

            # Agent Response
            with chat_container:
                with st.chat_message("assistant", avatar="🤖"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("🔄 *Analyzing logs...*")
                    
                    try:
                        model = genai.GenerativeModel('models/gemini-2.0-flash', tools=tools_list, system_instruction=system_instruction)
                        chat = model.start_chat(enable_automatic_function_calling=True)
                        response = chat.send_message(prompt)
                        message_placeholder.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                        
                        # Trigger visual alert if critical
                        if "HIGH" in response.text:
                            st.toast("⚠️ CRITICAL ALERT TRIGGERED!", icon="🔥")
                            
                    except Exception as e:
                        message_placeholder.error(f"Error: {e}")

with right_col:
    st.subheader("📡 Live Sensor Telemetry")
    
    # SIMULATED LIVE GRAPH
    # Create fake historical data to make it look "Alive"
    chart_data = pd.DataFrame(
        np.random.randn(20, 3) + [20, 45, 10],  # Fake baseline temps
        columns=['Pump-A', 'Pump-B', 'CNC-Fan']
    )
    st.line_chart(chart_data)
    
    st.info("Live Monitoring: CNC-01")
    
    # CRITICAL ALERT CARD
    st.error("""
    **🔥 CRITICAL WARNING: CNC-01**
    
    **Current Temp:** 105°C  (Limit: 100°C)
    **Vibration:** Critical
    **Status:** EMERGENCY STOP REQUESTED
    """)
    
    with st.expander("View Technical Logs"):
        st.code("""
        [10:42:01] SENSOR_READ: CNC-01 Temp=105C
        [10:42:02] ALERT: Threshold Exceeded (>100C)
        [10:42:02] AGENT: Emergency Stop Signal Sent
        [10:42:03] DB: Ticket #9928 Created
        """, language="bash")
