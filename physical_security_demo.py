import streamlit as st
import random
from datetime import datetime

st.set_page_config(
    page_title="Proactive Physical Security & Personalized Deterrence",
    layout="wide"
)

st.title("Proactive Physical Security & Personalized Deterrence (Demo)")
st.caption(
    "Simulated real-time surveillance analysis, threat scoring, deterrence response, and escalation workflow."
)

# ----------------------------
# Simulated Behavior Events
# ----------------------------

EVENTS = [
    "Normal movement",
    "Person loitering near gate",
    "Person moving in restricted area",
    "Abandoned object detected",
    "Attempt to climb fence",
    "Intrusion detected – unauthorized entry",
]

SEVERITY_MAP = {
    "Normal movement": "Low",
    "Person loitering near gate": "Medium",
    "Person moving in restricted area": "Medium",
    "Abandoned object detected": "Medium",
    "Attempt to climb fence": "High",
    "Intrusion detected – unauthorized entry": "High",
}

VOICE_RESPONSES = {
    "Low": "No response required.",
    "Medium": "Automated voice: 'This area is under surveillance. Please move away from the restricted zone.'",
    "High": "Automated voice: 'Security Alert! You are entering a restricted area. Leave immediately!'",
}

ESCALATION_MAP = {
    "Low": "No action required.",
    "Medium": "Monitoring continues.",
    "High": "Alert sent to nearest on-duty officer.",
}

# ----------------------------
# Sidebar Controls
# ----------------------------

with st.sidebar:
    st.header("Simulation Controls")
    st.markdown("Click the button to generate a new event.")
    generate_btn = st.button("🚀 Generate new event")

# ----------------------------
# State and helpers
# ----------------------------

if "logs" not in st.session_state:
    st.session_state.logs = []

def generate_event():
    event = random.choice(EVENTS)
    severity = SEVERITY_MAP[event]
    voice = VOICE_RESPONSES[severity]
    escalation = ESCALATION_MAP[severity]
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    st.session_state.logs.append({
        "time": ts,
        "event": event,
        "severity": severity,
        "voice": voice,
        "escalation": escalation,
    })

def display_latest():
    if not st.session_state.logs:
        return

    latest = st.session_state.logs[-1]
    event = latest["event"]
    severity = latest["severity"]
    voice = latest["voice"]
    escalation = latest["escalation"]
    ts = latest["time"]

    st.subheader(f"1️⃣ Real-Time Surveillance Event Stream")
    st.write(f"**Latest Event Time:** {ts}")
    st.write(f"**Detected Behavior:** {event}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Threat Assessment")
        if severity == "High":
            st.error(f"Severity: {severity}")
        elif severity == "Medium":
            st.warning(f"Severity: {severity}")
        else:
            st.success(f"Severity: {severity}")
    with col2:
        st.markdown("### Escalation")
        if severity == "High":
            st.error(escalation)
        else:
            st.write(escalation)

    st.markdown("### Automated Voice Response")
    st.info(voice)

# generate one event on first load so it is never empty
if not st.session_state.logs:
    generate_event()

if generate_btn:
    generate_event()

display_latest()

# ----------------------------
# Forensic event log
# ----------------------------

st.markdown("## 2️⃣ Forensic Event Log")

if st.session_state.logs:
    st.table(st.session_state.logs)
else:
    st.info("No events generated yet.")
