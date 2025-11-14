import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# -----------------------------
# Helpers to simulate log data
# -----------------------------


EVENT_TYPES = [
    "Normal traffic",
    "User login",
    "Failed login",
    "Port scan detected",
    "Unusual data upload",
    "Access from foreign IP",
    "Multiple failed logins",
    "Malware signature detected",
]

SEVERITY_LEVELS = ["Low", "Medium", "High"]


def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def generate_event(base_time: datetime) -> dict:
    event_type = random.choices(
        EVENT_TYPES,
        weights=[40, 20, 15, 5, 5, 5, 5, 5],  # more "normal" than "attack"
        k=1,
    )[0]

    if event_type in ["Normal traffic", "User login"]:
        severity = "Low"
    elif event_type in [
        "Failed login",
        "Port scan detected",
        "Unusual data upload",
    ]:
        severity = "Medium"
    else:
        severity = "High"

    return {
        "Timestamp": base_time,
        "Source IP": random_ip(),
        "Destination IP": random_ip(),
        "Event Type": event_type,
        "Severity": severity,
        "Details": generate_details(event_type),
    }


def generate_details(event_type: str) -> str:
    if event_type == "Failed login":
        return "3 consecutive failed logins for user ADMIN from unknown IP."
    if event_type == "Multiple failed logins":
        return "10+ failed logins within 1 minute – possible brute-force attack."
    if event_type == "Access from foreign IP":
        return "Access attempt from foreign IP not seen in last 30 days."
    if event_type == "Unusual data upload":
        return "Outbound traffic spike to external server."
    if event_type == "Port scan detected":
        return "Multiple ports probed from single IP."
    if event_type == "Malware signature detected":
        return "Known malware signature found in HTTP payload."
    if event_type == "User login":
        return "Successful user login."
    return "Regular background network traffic."


def init_events():
    """Initialise some past events for the demo."""
    now = datetime.utcnow()
    events = []
    for i in range(40):
        t = now - timedelta(minutes=40 - i)
        events.append(generate_event(t))
    return events


# -----------------------------
# Streamlit App
# -----------------------------

st.set_page_config(
    page_title="Threat Monitoring & Network Forensics Demo",
    layout="wide",
)

st.title("Real-Time Threat Monitoring & Network Forensics (Demo)")
st.caption(
    "Concept demo: Simulated view of alerts, anomalies and forensic logs for a "
    "government / enterprise network."
)

# Initialise session state
if "events" not in st.session_state:
    st.session_state.events = init_events()

# Sidebar controls
with st.sidebar:
    st.header("Simulation Controls")
    st.markdown("Generate new events to simulate **incoming traffic & attacks**.")

    num_new = st.slider("Number of new events", min_value=5, max_value=50, value=15)
    generate_btn = st.button("🚀 Generate new events")

    reset_btn = st.button("♻️ Reset simulation")

    st.markdown("---")
    show_only_high = st.checkbox("Show only High severity alerts", value=False)

if reset_btn:
    st.session_state.events = init_events()

if generate_btn:
    base_time = datetime.utcnow()
    for i in range(num_new):
        t = base_time + timedelta(seconds=i * 5)
        st.session_state.events.append(generate_event(t))
    st.success(f"Generated {num_new} new events.")

# Convert to DataFrame
df = pd.DataFrame(st.session_state.events)

# Filter if needed
if show_only_high:
    df_display = df[df["Severity"] == "High"].copy()
else:
    df_display = df.copy()

# Sort newest first for display
df_display = df_display.sort_values("Timestamp", ascending=False)

# -----------------------------
# Metrics Row
# -----------------------------
st.subheader("1️⃣ Network Security Summary")

total_events = len(df)
high_alerts = (df["Severity"] == "High").sum()
medium_alerts = (df["Severity"] == "Medium").sum()
unique_suspicious_ips = df[df["Severity"] == "High"]["Source IP"].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Events Observed", total_events)
with col2:
    st.metric("High Severity Alerts", int(high_alerts))
with col3:
    st.metric("Medium Severity Alerts", int(medium_alerts))
with col4:
    st.metric("Unique Suspicious Source IPs", int(unique_suspicious_ips))

# -----------------------------
# Time Series View
# -----------------------------
st.subheader("2️⃣ Activity Over Time (Events by Severity)")

df_ts = df.copy()
df_ts["Time (min)"] = df_ts["Timestamp"].dt.strftime("%H:%M")

severity_numeric = {"Low": 1, "Medium": 2, "High": 3}
df_ts["Severity Score"] = df_ts["Severity"].map(severity_numeric)

# Aggregate by minute
agg = df_ts.groupby(["Time (min)"]).agg(
    Events=("Event Type", "count"),
    AvgSeverity=("Severity Score", "mean"),
).reset_index()

st.line_chart(
    agg.set_index("Time (min)")[["Events", "AvgSeverity"]],
    use_container_width=True,
)

# -----------------------------
# Alerts & Forensic Log Table
# -----------------------------
st.subheader("3️⃣ Alerts & Forensic Log")

if df_display.empty:
    st.info("No events to display. Generate new events from the left panel.")
else:
    # Highlight most recent high severity alert
    last_high = (
        df[df["Severity"] == "High"]
        .sort_values("Timestamp", ascending=False)
        .head(1)
    )

    if not last_high.empty:
        last_event = last_high.iloc[0]
        st.warning(
            f"Most recent HIGH alert: **{last_event['Event Type']}** "
            f"from **{last_event['Source IP']}** at "
            f"{last_event['Timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}."
        )

    st.dataframe(
        df_display[
            [
                "Timestamp",
                "Source IP",
                "Destination IP",
                "Event Type",
                "Severity",
                "Details",
            ]
        ],
        use_container_width=True,
        height=400,
    )

st.markdown("---")
st.caption(
    "Demo only • Logs are simulated. In a real deployment, events would come from "
    "firewalls, servers, SIEM tools, and EDR/IDS systems, with deeper forensics."
)
