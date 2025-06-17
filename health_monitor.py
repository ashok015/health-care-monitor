import streamlit as st
import pandas as pd
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime

# -------------------------
# Function to generate vitals
# -------------------------
def generate_sample_data():
    return {
        "Heart Rate": random.randint(55, 135),
        "BP Systolic": random.randint(95, 175),
        "BP Diastolic": random.randint(65, 105),
        "Temperature": round(random.uniform(36.2, 39.8), 1),
        "Glucose": random.randint(80, 230),
        "SpO2": random.randint(88, 100)
    }

# -------------------------
# Evaluate health status
# -------------------------
def evaluate_status(vitals):
    issues = 0
    if vitals['Heart Rate'] < 60 or vitals['Heart Rate'] > 120:
        issues += 1
    if vitals['BP Systolic'] > 140 or vitals['BP Diastolic'] > 90:
        issues += 1
    if vitals['Temperature'] > 38.5:
        issues += 1
    if vitals['Glucose'] > 180:
        issues += 1
    if vitals['SpO2'] < 92:
        issues += 1

    if issues == 0:
        return "Normal"
    elif issues <= 2:
        return "Warning"
    else:
        return "Critical"

# -------------------------
# Send email alert
# -------------------------
def send_email_alert(vitals, receiver_email, user_name):
    EMAIL_ADDRESS = st.secrets["credentials"]["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = st.secrets["credentials"]["EMAIL_PASSWORD"]

    msg = EmailMessage()
    msg['Subject'] = "Critical Health Alert"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = receiver_email

    content = f"""
    A critical health condition has been detected.

    Patient Name: {user_name}
    Email: {receiver_email}

    Vitals:
    - Heart Rate: {vitals['Heart Rate']} bpm
    - Blood Pressure: {vitals['BP Systolic']}/{vitals['BP Diastolic']}
    - Temperature: {vitals['Temperature']} °C
    - Glucose: {vitals['Glucose']} mg/dL
    - SpO2: {vitals['SpO2']} %

    Please consult a healthcare provider.
    """
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Health Monitor", layout="wide")
st.title("Health Monitoring System")

# Step 1: User inputs
if 'user_name' not in st.session_state:
    with st.form("user_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address (to receive alerts)")
        submitted = st.form_submit_button("Submit & Start")

        if submitted and name and email:
            st.session_state.user_name = name
            st.session_state.user_email = email
            st.success("Details saved. You can now monitor vitals.")

# Step 2: Generate data and monitor
if 'user_name' in st.session_state and 'user_email' in st.session_state:
    if 'record_log' not in st.session_state:
        st.session_state['record_log'] = []

    if st.button("Generate Health Reading"):
        vitals = generate_sample_data()
        status = evaluate_status(vitals)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "Timestamp": timestamp,
            **vitals,
            "Status": status
        }
        st.session_state['record_log'].append(record)

        st.subheader(f"Status: {status}")
        st.dataframe(pd.DataFrame([record]))

        if status == "Critical":
            if send_email_alert(vitals, st.session_state.user_email, st.session_state.user_name):
                st.error("Critical alert email sent to user.")
            else:
                st.warning("Failed to send email.")

    if st.session_state['record_log']:
        st.subheader("Monitoring Log")
        df = pd.DataFrame(st.session_state['record_log'])
        st.dataframe(df)
        st.download_button("Download Log", df.to_csv(index=False), file_name="health_log.csv")
