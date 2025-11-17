import streamlit as st
import random
import time
from datetime import datetime

st.set_page_config(
    page_title="Proactive Physical Security & Personalized Deterrence",
    layout="wide"
)

st.title("Proactive Physical Security & Personalized Deterrence (Demo)")
st.caption("Simulated real-time surveillance analysis, threat scoring, deterrence response, and escalation workflow.")

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
    "Medium": "Automated Voice: 'This area is being monitored. Please move away from the restricted zone.'",
    "High": "Automated Voice: 'Security Alert! You are entering a restricted area. Leave immediately!'"
}

ESCALATION_MAP = {
    "Low": "No action.",
    "Medium": "Monitoring continues.",
    "High": "Alert sent to nearest on-duty officer."
}

# ----------------------------
# Sidebar Simulation Controls
# ----------------------------

with st.sidebar:
    st.header("Simulation Controls")
    speed = st.slider("Event generation speed (seconds)", 1, 10, 3)
    auto_run = st.checkbox("Auto-generate events continuously")
    manual_event = st.button("Generate one event manually")

st.markdown("## 1️⃣ Real-Time Surveillance Event Stream")

event_placeholder = st.empty()
severity_placeholder = st.empty()
voice_placeholder = st.empty()
escalation_placeholder = st.empty()
log_placeholder = st.empty()

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
        "escalation": escalation
    })

    return event, severity, voice, escalation, ts

def display_latest():
    event, severity, voice, escalation, ts = st.session_state.logs[-1]

    event_placeholder.subheader(f"🕒 Latest Event: {ts}")
    event_placeholder.write(f"**Detected Behavior:** {event}")

    severity_placeholder.subheader("Threat Assessment")
    if severity == "High":
        severity_placeholder.error(f"Severity: {severity}")
    elif severity == "Medium":
        severity_placeholder.warning(f"Severity: {severity}")
    else:
        severity_placeholder.success(f"Severity: {severity}")

    voice_placeholder.subheader("Automated Voice Response")
    voice_placeholder.info(voice)

    escalation_placeholder.subheader("Escalation")
    if severity == "High":
        escalation_placeholder.error(escalation)
    else:
        escalation_placeholder.write(escalation)

# ----------------------------
# Live Simulation Loop
# ----------------------------

if auto_run:
    while True:
        generate_event()
        display_latest()
        time.sleep(speed)

if manual_event:
    generate_event()
    display_latest()

# ----------------------------
# Forensic Log Table
# ----------------------------

st.markdown("## 2️⃣ Forensic Event Log")
log_placeholder.table(st.session_state.logs)
