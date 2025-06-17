# ============================================
# 🩺 HEALTH CARE MONITOR - STREAMLIT APP (FINAL - HUMANIZED CODE)
# ============================================

import streamlit as st
import pandas as pd
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime

# -----------------------------
# EMAIL ALERT SETTINGS
# -----------------------------
EMAIL_ADDRESS = "your_email@gmail.com"  # Replace this with sender email
EMAIL_PASSWORD = "your_app_password"    # Use an app-specific password
ALERT_RECEIVER = "receiver_email@gmail.com"  # Recipient's email address

# -----------------------------
# GENERATE SAMPLE HEALTH DATA
# -----------------------------
def generate_sample_data():
    return {
        "Heart Rate": 150,  # Critical
        "BP Systolic": 180,  # Critical
        "BP Diastolic": 100,
        "Temperature": 39.5,
        "Glucose": 250,
        "SpO2": 88  # Critical
    }


# -----------------------------
# EVALUATE HEALTH STATUS BASED ON DATA
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
# SEND EMAIL NOTIFICATION IF STATUS IS CRITICAL
# -----------------------------
def send_email(vitals):
    from email.message import EmailMessage
    import smtplib
    import streamlit as st

    # Load credentials
    sender_email = st.secrets["credentials"]["email"]
    app_password = st.secrets["credentials"]["password"]
    receiver_email = st.secrets["credentials"]["receiver"]

    # Prepare the email message
    msg = EmailMessage()
    msg['Subject'] = 'Health Alert: Critical Vitals Detected'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    msg.set_content(f"""
    Hello,

    A patient has shown critical signs in their health monitoring report.

    Vitals Report:
    - Heart Rate     : {vitals['Heart Rate']} bpm
    - Blood Pressure : {vitals['BP Systolic']}/{vitals['BP Diastolic']} mmHg
    - Temperature    : {vitals['Temperature']} °C
    - Glucose Level  : {vitals['Glucose']} mg/dL
    - SpO2           : {vitals['SpO2']}%

    Immediate attention is advised.

    Regards,
    Health Monitoring System
    """)

    try:


# -----------------------------
# STREAMLIT DASHBOARD UI
# -----------------------------
st.set_page_config(page_title="Health Monitor", layout="wide")
st.title("🩺 Health Monitoring Dashboard")

if 'record_log' not in st.session_state:
    st.session_state['record_log'] = []

if st.button("Generate Reading"):
    vitals = generate_sample_data()
    status = evaluate_status(vitals)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "Timestamp": timestamp,
        **vitals,
        "Status": status
    }
    st.session_state['record_log'].append(entry)

    st.subheader(f"Patient Status: {status}")
    st.dataframe(pd.DataFrame([entry]))

    if status == "Critical":
        send_email(vitals)
        st.error("Email Notification Sent!")

if st.session_state['record_log']:
    st.subheader("Health Monitoring Log")
    logs_df = pd.DataFrame(st.session_state['record_log'])
    st.dataframe(logs_df)

    if st.download_button("Download Log", logs_df.to_csv(index=False).encode(), file_name='monitoring_log.csv'):
        st.success("Log file is ready for download.")
