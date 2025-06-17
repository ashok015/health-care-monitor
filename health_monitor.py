# ==========================================
# Health Monitoring Dashboard - Streamlit App
# ==========================================

import streamlit as st
import pandas as pd
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime

# -----------------------------
# Email Alert Configuration
# -----------------------------
def send_email(vitals, receiver_email, user_name):
    try:
        EMAIL_ADDRESS = st.secrets["credentials"]["email"]
        EMAIL_PASSWORD = st.secrets["credentials"]["password"]

        msg = EmailMessage()
        msg["Subject"] = f"{user_name}, Health Alert Notification"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver_email

        body = f"""
        Hello {user_name},

        A critical health condition has been detected based on the following readings:

        - Heart Rate: {vitals['Heart Rate']} bpm
        - Blood Pressure: {vitals['BP Systolic']}/{vitals['BP Diastolic']} mmHg
        - Temperature: {vitals['Temperature']} °C
        - Glucose Level: {vitals['Glucose']} mg/dL
        - SpO2: {vitals['SpO2']} %

        Please consult a medical professional immediately if you experience any symptoms.

        Regards,
        Health Monitoring System
        """
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        st.success("Email alert successfully sent.")

    except Exception as e:
        st.error(f"Failed to send email: {e}")

# -----------------------------
# Generate Sample Health Data
# -----------------------------
def generate_sample_data():
    return {
        "Heart Rate": random.randint(55, 135),
        "BP Systolic": random.randint(95, 175),
        "BP Diastolic": random.randint(65, 105),
        "Temperature": round(random.uniform(36.2, 39.8), 1),
        "Glucose": random.randint(80, 230),
        "SpO2": random.randint(88, 100)
    }

# -----------------------------
# Evaluate Health Status
# -----------------------------
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

# -----------------------------
# Streamlit App Configuration
# -----------------------------
st.set_page_config(page_title="Health Monitor", layout="wide")
st.title("Health Monitoring Dashboard")

# User Input
with st.form("user_info_form"):
    st.subheader("Enter User Details")
    user_name = st.text_input("Full Name")
    user_email = st.text_input("Email Address")
    submitted = st.form_submit_button("Start Monitoring")

if not submitted or not user_email:
    st.warning("Please provide your name and email address to continue.")
    st.stop()

# Session State to Log Data
if 'record_log' not in st.session_state:
    st.session_state['record_log'] = []

# Generate Readings
if st.button("Generate Health Data"):
    vitals = generate_sample_data()
    status = evaluate_status(vitals)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "Timestamp": timestamp,
        **vitals,
        "Status": status
    }
    st.session_state['record_log'].append(entry)

    st.subheader(f"Current Health Status: {status}")
    st.dataframe(pd.DataFrame([entry]))

    if status == "Critical":
        send_email(vitals, user_email, user_name)

# Display Log History
if st.session_state['record_log']:
    st.subheader("Health Monitoring Records")
    logs_df = pd.DataFrame(st.session_state['record_log'])
    st.dataframe(logs_df)

    st.download_button("Download Records", logs_df.to_csv(index=False).encode(), file_name='monitoring_log.csv')
