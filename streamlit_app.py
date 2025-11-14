import streamlit as st
import pandas as pd
import re

# -----------------------------
# Simple Rule-Based Classifier
# -----------------------------

CRIME_KEYWORDS = {
    "Social Media Harassment": [
        "instagram", "facebook", "twitter", "x.com", "snapchat",
        "social media", "profile", "story", "reel", "dm", "direct message",
        "troll", "abuse", "harass", "stalking", "stalker"
    ],
    "Online Financial Fraud / Phishing": [
        "otp", "one time password", "bank", "upi", "gpay", "phonepe", "paytm",
        "credit card", "debit card", "loan", "kbc", "lottery", "prize",
        "fake link", "phishing", "fraud", "payment", "investment", "trading",
        "crypto", "bitcoin"
    ],
    "Identity Theft / Account Takeover": [
        "hacked", "account taken", "login", "password", "credential",
        "sim swap", "sim-swapping", "email hacked", "whatsapp hacked",
        "telegram hacked"
    ],
    "Cyber Bullying / Threats": [
        "threat", "blackmail", "morphed", "nude", "leak", "compromise",
        "insult", "abusive", "defame", "revenge porn"
    ],
    "Job / Recruitment Scam": [
        "job offer", "placement", "recruitment", "hr", "work from home",
        "data entry", "typing job"
    ],
    "Other / General Cybercrime": []
}

HIGH_PRIORITY_PATTERNS = [
    r"threaten", r"blackmail", r"kill", r"murder", r"revenge porn",
    r"minor", r"child", r"rape", r"sexual", r"life in danger",
    r"suicide", r"extort", r"extortion"
]

MEDIUM_PRIORITY_PATTERNS = [
    r"hacked", r"account taken", r"lost money", r"withdrawn",
    r"fraud", r"phishing", r"scam", r"harass", r"stalking"
]


def classify_crime_type(text: str) -> str:
    text_l = text.lower()
    scores = {k: 0 for k in CRIME_KEYWORDS.keys()}

    for crime_type, keywords in CRIME_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l:
                scores[crime_type] += 1

    # If everything is zero -> Other / General Cybercrime
    if all(v == 0 for v in scores.values()):
        return "Other / General Cybercrime"

    # Return crime type with max score
    return max(scores, key=scores.get)


def classify_priority(text: str) -> str:
    text_l = text.lower()

    for pattern in HIGH_PRIORITY_PATTERNS:
        if re.search(pattern, text_l):
            return "High"

    for pattern in MEDIUM_PRIORITY_PATTERNS:
        if re.search(pattern, text_l):
            return "Medium"

    return "Low"


def suggest_unit(crime_type: str) -> str:
    if "Harassment" in crime_type or "Bullying" in crime_type:
        return "Women’s Safety / Cyber Harassment Cell"
    if "Financial Fraud" in crime_type or "Phishing" in crime_type:
        return "Cyber Financial Fraud Unit"
    if "Identity Theft" in crime_type or "Account Takeover" in crime_type:
        return "Cyber Crime Investigation Unit"
    if "Job / Recruitment Scam" in crime_type:
        return "Economic Offences / Cyber Fraud Unit"
    return "General Cyber Crime Cell"


# ----------------------------------
# Streamlit App: UI & Demo Workflow
# ----------------------------------

st.set_page_config(
    page_title="AI-Based Cybercrime Case Triage Demo",
    layout="wide",
)

st.title("AI-Based Cybercrime Case Triage System (Demo)")
st.caption(
    "Concept demo: Automatically classify and prioritize cybercrime complaints "
    "to reduce backlog in government cyber cells."
)

# Initialize session state for case list
if "cases" not in st.session_state:
    st.session_state.cases = []

# Example complaints (you can tweak these)
EXAMPLE_COMPLAINTS = [
    "Someone hacked my Instagram account and is threatening to leak my photos if I don't pay.",
    "I received a fake bank SMS asking for my OTP, and after entering it, money was debited from my account.",
    "Unknown person is continuously calling and sending abusive WhatsApp messages to my daughter.",
    "I saw a work from home job offer on Telegram, paid a registration fee and then they blocked me.",
    "My email and Facebook accounts were hacked and the attacker is messaging my contacts.",
    "Our office computer received multiple login attempts from an unknown foreign IP.",
]

with st.sidebar:
    st.header("Demo Controls")
    st.markdown("Choose a **sample complaint** or type your own case below:")
    selected_example = st.selectbox(
        "Sample complaints",
        options=["(None – I will type my own)"] + EXAMPLE_COMPLAINTS,
        index=0
    )

    clear_btn = st.button("Clear All Cases")

    if clear_btn:
        st.session_state.cases = []

# Main input area
st.subheader("1️⃣ Enter or Select a Cybercrime Complaint")

default_text = "" if selected_example == "(None – I will type my own)" else selected_example

complaint_text = st.text_area(
    "Complaint Description",
    value=default_text,
    height=150,
    help="Paste or type the actual text of the complaint here."
)

col1, col2 = st.columns([1, 3])

with col1:
    add_case = st.button("➕ Analyze & Add to Queue")

with col2:
    st.write("")  # spacing

if add_case and complaint_text.strip():
    crime_type = classify_crime_type(complaint_text)
    priority = classify_priority(complaint_text)
    unit = suggest_unit(crime_type)

    case_id = len(st.session_state.cases) + 1
    st.session_state.cases.append({
        "Case ID": f"C-{case_id:03d}",
        "Complaint": complaint_text.strip(),
        "Crime Type": crime_type,
        "Priority": priority,
        "Suggested Unit": unit,
    })
    st.success(f"Case added and classified as **{crime_type}** (Priority: **{priority}**).")

# Display dashboard
st.subheader("2️⃣ Triage Dashboard – Prioritised Case View")

if not st.session_state.cases:
    st.info("No cases yet. Add a complaint above to see the triage dashboard.")
else:
    df = pd.DataFrame(st.session_state.cases)

    # Sort by priority (High > Medium > Low)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    df["PriorityRank"] = df["Priority"].map(priority_order)
    df = df.sort_values(by=["PriorityRank", "Case ID"]).drop(columns=["PriorityRank"])

    # Summary metrics
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Cases", len(df))
    with col_b:
        st.metric("High Priority", int((df["Priority"] == "High").sum()))
    with col_c:
        st.metric("Medium Priority", int((df["Priority"] == "Medium").sum()))

    st.dataframe(
        df[["Case ID", "Complaint", "Crime Type", "Priority", "Suggested Unit"]],
        use_container_width=True,
        height=400
    )

st.markdown("---")
st.caption(
    "Demo only • Rules can be replaced with an actual AI/NLP model (Gemini, OpenAI, "
    "or Hugging Face) and integrated with real complaint systems and case management."
)

